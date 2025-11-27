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
import time
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
latest_summary: Dict[str, object] = {
    "timestamp": None,
    "total": 0,
    "counts": {},
}


def choose_device(pref: str) -> str:
    if pref != "auto":
        return pref
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def open_capture(source: str) -> cv2.VideoCapture:
    if source.isdigit():
        cap = cv2.VideoCapture(int(source))
    else:
        cap = cv2.VideoCapture(source)
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


def frame_generator(conf: float, imgsz: int, labels_of_interest):
    assert cap is not None and model is not None
    global latest_summary
    while True:
        ok, frame = cap.read()
        if not ok:
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
        latest_summary = {
            **build_summary(r0, labels_of_interest),
            "timestamp": time.time(),
        }
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

    global model, cap, predict_device
    model = YOLO(args.weights).to(device)
    predict_device = None if device in ("cpu", "mps") else 0
    cap = open_capture(args.source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not cap.isOpened():
        raise SystemExit("Could not open camera/source. Check permissions or index.")

    app.config["CONF"] = args.conf
    app.config["IMGSZ"] = args.imgsz
    app.config["LABELS"] = args.health_labels

    atexit.register(cleanup)
    app.run(host=args.host, port=args.port, threaded=True)


if __name__ == "__main__":
    main()
