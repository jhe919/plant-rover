import cv2

# 0 is the default camera index; try 1 or 2 if you have multiple cameras.
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError(
        "Camera not found or permission denied. On macOS: System Settings → Privacy & Security → Camera → "
        "enable access for your Terminal/VS Code."
    )

# Optional: set a smaller resolution if you want higher FPS
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    cv2.imshow("Camera test (ESC to quit)", frame)

    # Check for ESC key
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
