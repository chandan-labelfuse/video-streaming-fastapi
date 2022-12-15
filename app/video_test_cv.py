import cv2

cam = "videos/video1.mp4"
cap = cv2.VideoCapture(cam)

while True:

    success, frame = cap.read()
    if not success:
        break
    else:
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
