import cv2
from picamera2 import Picamera2
from ultralytics import YOLO

MODEL = "../weights/plantdetector.onnx"
CONF = 0.35
model = YOLO(MODEL)  # uses onnxruntime backend

picam = Picamera2()
cfg = picam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
picam.configure(cfg); picam.start()

print("ESC to quit")
while True:
    frame = picam.capture_array()  # 640x480 RGB
    r = model.predict(frame, conf=CONF, imgsz=480, verbose=False)[0]
    annotated = r.plot()
    cv2.putText(annotated, "Pi rpicam + ONNX", (12,28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.imshow("Plant detector (Pi)", annotated)
    if cv2.waitKey(1) & 0xFF == 27: break
picam.close(); cv2.destroyAllWindows()
