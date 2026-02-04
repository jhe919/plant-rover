#!/usr/bin/env python3
"""
Flask-based bridge that streams the YOLO health detector to the RoverUI frontend.

Run:
    python src/ui_stream_server.py \
        --weights runs/health/yolov8n_health_fast/weights/best.pt \
        --conf 0.3 \
        --source 0

Then point the UI (Vite dev server) at http://localhost:8000/video_feed.
"""
from __future__ import annotations

import argparse
import atexit
import json
import time
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Dict, Generator, Optional

import cv2
import torch
from flask import Flask, Response, jsonify
from flask_cors import CORS
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

cap: Optional[cv2.VideoCapture] = None
model: Optional[YOLO] = None
predict_device: Optional[int] = None
picam2 = None
latest_summary: Dict[str, object] = {
    "timestamp": None,
    "total": 0,
    "counts": {},
}
last_command_time = 0.0


def choose_device(pref: str) -> str:
    if pref != "auto":
        return pref
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def open_capture(source: str, backend: str, width: Optional[int], height: Optional[int]) -> cv2.VideoCapture:
    api = cv2.CAP_V4L2 if backend == "v4l2" else 0
    if source.isdigit():
        cap = cv2.VideoCapture(int(source), api)
    else:
        cap = cv2.VideoCapture(source, api)
    if width:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    if height:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap


def build_summary(result, labels_of_interest):
    boxes = getattr(result, "boxes", None)
    counts = Counter()
    if boxes is not None and len(boxes) > 0:
        names = result.names if isinstance(result.names, dict) else {i: n for i, n in enumerate(result.names)}
        for cls_id in boxes.cls.tolist():
            label = names.get(int(cls_id), str(int(cls_id)))
            counts[label] += 1
    out = {"total": sum(counts.values()), "counts": dict(counts)}
    if labels_of_interest:
        out["counts_subset"] = {label: counts.get(label, 0) for label in labels_of_interest}
    return out


def best_box_center_x(result) -> Optional[float]:
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(boxes) == 0:
        return None
    # Choose the highest-confidence box to represent the target.
    confs = boxes.conf.tolist()
    idx = max(range(len(confs)), key=lambda i: confs[i])
    x1, y1, x2, y2 = boxes.xyxy[idx].tolist()
    return (x1 + x2) / 2.0


def frame_generator(conf: float, imgsz: int, labels_of_interest):
    assert model is not None
    global latest_summary, last_command_time
    while True:
        if picam2 is not None:
            try:
                frame = picam2.capture_array()
            except Exception:
                time.sleep(0.05)
                continue
            ok = frame is not None and getattr(frame, "size", 0) > 0
            if ok:
                # picamera2 gives RGB; convert to BGR for OpenCV/YOLO
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            ok, frame = cap.read()
        if not ok or frame is None or frame.size == 0:
            time.sleep(0.05)
            continue
        results = model.predict(
            source=frame,
            conf=conf,
            verbose=False,
            imgsz=imgsz,
            device=predict_device,
        )
        r0 = results[0]
        annotated = r0.plot()
        x_center = best_box_center_x(r0)
        bbox_width = None
        if x_center is not None:
            confs = r0.boxes.conf.tolist()
            idx = max(range(len(confs)), key=lambda i: confs[i])
            x1, y1, x2, y2 = r0.boxes.xyxy[idx].tolist()
            bbox_width = max(0.0, x2 - x1)
        latest_summary = {
            **build_summary(r0, labels_of_interest),
            "timestamp": time.time(),
            "bbox_center_x": x_center,
            "bbox_width": bbox_width,
        }
        if app.config.get("COMMAND_URL"):
            now = time.time()
            cooldown = app.config.get("COMMAND_COOLDOWN", 2.0)
            if app.config.get("SEND_X"):
                x_center = best_box_center_x(r0)
                if x_center is not None and (now - last_command_time) >= cooldown:
                    frame_width = r0.orig_shape[1]
                    x_norm = x_center / max(frame_width, 1)
                    scale = app.config.get("X_SCALE", 1000)
                    cmd = f"X {int(x_norm * scale)}"
                    payload = {
                        "cmd": cmd,
                        "x_norm": x_norm,
                        "scale": scale,
                        "bbox_center_x": latest_summary.get("bbox_center_x"),
                        "bbox_width": latest_summary.get("bbox_width"),
                        "counts": latest_summary.get("counts", {}),
                    }
                    try:
                        req = urllib.request.Request(
                            app.config["COMMAND_URL"],
                            data=json.dumps(payload).encode("utf-8"),
                            headers={"Content-Type": "application/json"},
                        )
                        urllib.request.urlopen(req, timeout=0.5)
                    except Exception:
                        pass
                    last_command_time = now
            else:
                unhealthy = latest_summary.get("counts", {}).get("unhealthy", 0)
                threshold = app.config.get("UNHEALTHY_THRESHOLD", 1)
                if unhealthy >= threshold and (now - last_command_time) >= cooldown:
                    payload = {
                        "cmd": app.config.get("COMMAND", "STOP"),
                        "counts": latest_summary.get("counts", {}),
                        "total": latest_summary.get("total", 0),
                    }
                    try:
                        req = urllib.request.Request(
                            app.config["COMMAND_URL"],
                            data=json.dumps(payload).encode("utf-8"),
                            headers={"Content-Type": "application/json"},
                        )
                        urllib.request.urlopen(req, timeout=0.5)
                    except Exception:
                        pass
                    last_command_time = now
        ok, buffer = cv2.imencode(".jpg", annotated)
        if not ok:
            continue
        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.route("/video_feed")
def video_feed():
    return Response(
        frame_generator(
            conf=app.config["CONF"],
            imgsz=app.config["IMGSZ"],
            labels_of_interest=app.config["LABELS"],
        ),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/health")
def health_summary():
    return jsonify(latest_summary)


@app.route("/")
def index():
    return jsonify({"status": "ok", "endpoints": ["/video_feed", "/health"]})


def cleanup():
    if cap is not None:
        cap.release()


def parse_args():
    ap = argparse.ArgumentParser(description="Stream YOLO detections to RoverUI.")
    ap.add_argument("--weights", type=Path, required=True,
                    help="Path to trained YOLO weights (.pt).")
    ap.add_argument("--source", default="0",
                    help="Camera index or video path/URL.")
    ap.add_argument("--conf", type=float, default=0.3,
                    help="Confidence threshold.")
    ap.add_argument("--imgsz", type=int, default=640,
                    help="Inference image size.")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda", "mps"], default="auto")
    ap.add_argument("--backend", choices=["auto", "v4l2"], default="auto",
                    help="Preferred OpenCV backend (use v4l2 on Raspberry Pi).")
    ap.add_argument("--width", type=int, default=None,
                    help="Optional capture width.")
    ap.add_argument("--height", type=int, default=None,
                    help="Optional capture height.")
    ap.add_argument("--picamera2", action="store_true",
                    help="Use Picamera2 for capture (recommended on Pi if V4L2 frames fail).")
    ap.add_argument("--command-url", default=None,
                    help="Optional HTTP endpoint (Pi bridge) to send commands when unhealthy plants detected.")
    ap.add_argument("--command", default="STOP",
                    help="Command text to send when threshold is hit.")
    ap.add_argument("--unhealthy-threshold", type=int, default=1,
                    help="Minimum unhealthy detections required to emit a command.")
    ap.add_argument("--command-cooldown", type=float, default=2.0,
                    help="Seconds to wait between command sends.")
    ap.add_argument("--send-x", action="store_true",
                    help="Send target box center x as 'X <value>' to the command URL.")
    ap.add_argument("--x-scale", type=int, default=1000,
                    help="Scale for normalized x (0..1) when sending X command.")
    ap.add_argument("--health-labels", nargs="*", default=["healthy", "unhealthy"],
                    help="Subset of labels to highlight in the summary endpoint.")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    return ap.parse_args()


def main():
    args = parse_args()
    if not args.weights.exists():
        raise SystemExit(f"Weights not found: {args.weights}")

    device = choose_device(args.device)
    print(f"[ui-stream] Using device={device}")

    global model, cap, predict_device, picam2
    model = YOLO(args.weights).to(device)
    predict_device = None if device in ("cpu", "mps") else 0
    if args.picamera2:
        try:
            from picamera2 import Picamera2
        except ImportError as e:
            raise SystemExit("Picamera2 not installed. Try: sudo apt install python3-picamera2") from e
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (args.width or 1280, args.height or 720), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()
    else:
        cap = open_capture(args.source, backend=args.backend, width=args.width, height=args.height)
        if not cap.isOpened():
            raise SystemExit("Could not open camera/source. Check permissions or index.")

    app.config["CONF"] = args.conf
    app.config["IMGSZ"] = args.imgsz
    app.config["LABELS"] = args.health_labels
    app.config["COMMAND_URL"] = args.command_url
    app.config["COMMAND"] = args.command
    app.config["UNHEALTHY_THRESHOLD"] = args.unhealthy_threshold
    app.config["COMMAND_COOLDOWN"] = args.command_cooldown
    app.config["SEND_X"] = args.send_x
    app.config["X_SCALE"] = args.x_scale

    atexit.register(cleanup)
    app.run(host=args.host, port=args.port, threaded=True)


if __name__ == "__main__":
    main()
