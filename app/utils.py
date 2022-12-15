from queue import Queue
from threading import Thread

import cv2


class CamStream:
    def __init__(self, src):

        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        self.stopped = False

        self.queue = Queue(120)

        self.t = Thread(target=self.update, args=())
        self.t.daemon = True

    def start(self):

        self.stopped = False
        self.t.start()

    def update(self):

        while True:
            if self.stopped:
                break

            (self.grabbed, self.frame) = self.stream.read()
            self.queue.put(self.frame)

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


def gen_frames_threading(CamStream):

    while True:
        frame = CamStream.queue.get()
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


def gen_frames(cam):

    cap = cv2.VideoCapture(cam)

    while True:

        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )


def get_camera_list(db_camera_list):
    camera_list = []
    for c in db_camera_list:
        camera_list.append(tuple(c.values())[1])

    if len(camera_list) > 0:
        return camera_list
    return []


def find_camera(camera_id, db_camera_list):
    camera_list = []
    for c in db_camera_list:
        camera_list.append(tuple(c.values())[1])

    if len(camera_list) > 0:
        return camera_list[camera_id]
    return []
