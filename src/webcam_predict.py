#!/usr/bin/env python3
import argparse
from collections import Counter

import cv2
import torch
from ultralytics import YOLO


def parse_args():
    ap = argparse.ArgumentParser(description="Run the webcam model with health summary overlays.")
    ap.add_argument("--weights", default="runs/detect/plantdoc_n480/weights/best.pt",
                    help="Path to YOLO weights file (.pt).")
    ap.add_argument("--source", default="0",
                    help="Camera index (e.g. 0/1) or path/URL understood by OpenCV.")
    ap.add_argument("--conf", type=float, default=0.25,
                    help="Confidence threshold.")
    ap.add_argument("--imgsz", type=int, default=640, help="Inference image size.")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda", "mps"], default="auto")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--health-labels", nargs="*", default=["healthy", "unhealthy"],
                    help="Labels to highlight in the HUD. Use actual class names from your model.")
    return ap.parse_args()


def choose_device(pref: str) -> str:
    if pref != "auto":
        return pref
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def open_capture(source_str: str) -> cv2.VideoCapture:
    if source_str.isdigit():
        cap = cv2.VideoCapture(int(source_str))
    else:
        cap = cv2.VideoCapture(source_str)
    return cap


def build_summary(result, labels_of_interest):
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(boxes) == 0:
        return "No detections"

    counts = Counter()
    names = result.names if isinstance(result.names, dict) else {i: n for i, n in enumerate(result.names)}
    for cls_id in boxes.cls.tolist():
        label = names.get(int(cls_id), str(int(cls_id)))
        counts[label] += 1

    parts = []
    if labels_of_interest:
        for label in labels_of_interest:
            parts.append(f"{label}:{counts.get(label, 0)}")
    parts.append(f"total:{len(boxes.cls)}")
    return " | ".join(parts)


def main():
    args = parse_args()
    device = choose_device(args.device)
    model = YOLO(args.weights).to(device)

    cap = open_capture(args.source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera. Try a different index (1/2) or grant permissions.")

    predict_device = None if device in ("cpu", "mps") else 0
    window = "Plant Rover - Webcam"

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        results = model.predict(
            source=frame,
            conf=args.conf,
            verbose=False,
            imgsz=args.imgsz,
            device=predict_device,
        )
        r0 = results[0]
        annotated = r0.plot()
        hud_summary = build_summary(r0, args.health_labels)
        footer = f"{hud_summary} || device={device} conf>{args.conf}"
        cv2.putText(
            annotated, footer, (12, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2
        )
        cv2.imshow(window, annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
