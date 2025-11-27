import os
import time
import cv2
import torch
from ultralytics import YOLO

# Pick the best available device: Apple GPU (mps) > CUDA > CPU
device = (
    "mps" if torch.backends.mps.is_available()
    else ("cuda" if torch.cuda.is_available() else "cpu")
)

# Load a tiny pre-trained model (downloads on first run)
model = YOLO("yolov8n.pt").to(device)

# Confidence threshold: higher = fewer, more-confident boxes
CONF = 0.4

# Open webcam and set a reasonable resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    raise RuntimeError(
        "Camera not found or permission denied. On macOS: System Settings → Privacy & Security → Camera → "
        "enable access for your Terminal/VS Code."
    )

while True:
    ok, frame = cap.read()
    if not ok:
        break

    # Run YOLO on the current frame.
    # Note: passing device here only matters for CUDA; MPS is picked via model.to(device).
    results = model.predict(
        source=frame,
        conf=CONF,
        verbose=False,
        device=0 if (device != "cpu" and device != "mps") else None
    )

    r = results[0]           # batch size = 1, so take the first result
    annotated = r.plot()     # Ultralytics helper: draws boxes/labels on a copy
    any_object = len(r.boxes) > 0

    # Heads-up display text
    hud = f"Object present: {'YES' if any_object else 'NO'} | conf>{CONF} | device={device}"
    cv2.putText(
        annotated, hud, (12, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2
    )

    cv2.imshow("YOLO live (S: save frame, ESC: quit)", annotated)
    key = cv2.waitKey(1) & 0xFF

    # Press 's' to save the raw (unannotated) frame for your dataset
    if key == ord('s'):
        os.makedirs("data/raw", exist_ok=True)
        path = f"data/raw/frame_{int(time.time()*1000)}.jpg"
        cv2.imwrite(path, frame)
        print("Saved", path)

    if key == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()