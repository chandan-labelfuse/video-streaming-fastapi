from queue import Queue
from threading import Thread

import cv2
import numpy as np
import tritonclient.grpc as grpcclient
from PIL import Image

from utils.yolov4.processing import preprocess, postprocess
from utils.yolov4.labels import COCOLabels
from utils.yolov4.render import render_box, render_filled_box, get_text_size, render_text, RAND_COLORS
from utils.yolov4.grpctritonclient import create_client

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


class CamStreamTriton:
    def __init__(self, src, url):

        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        self.stopped = False

        self.triton_client = create_client(url=url)

        self.inputs = []
        self.outputs = []

        self.queue = Queue(120)

        self.t = Thread(target=self.update, args=())
        self.t.daemon = True

    def start(self):

        self.inputs.append(grpcclient.InferInput('input', [1, 3, 608, 608], "FP32"))
        self.outputs.append(grpcclient.InferRequestedOutput('detections'))

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


class CamStreamTorch:
    def __init__(self, src):

        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        self.stopped = False

        self.queue = Queue(120)

        self.t = Thread(target=self.update, args=())
        self.t.daemon = True

        self.model = get_ssd_model()
        self.preprocess = get_ssd_preprocess()

        self.device = torch.device('cuda')

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


def gen_frames_threading_ssd(CamStreamTorch):
    while True:
        frame = CamStreamTorch.queue.get()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        
        batch = CamStreamTorch.preprocess(image)
        batch = torch.unsqueeze(batch, dim=0)
        batch = batch.to(CamStreamTorch.device)

        prediction = CamStreamTorch.model(batch)[0]

        frame = ssd_postprocess(prediction, frame)

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


def gen_frames_threading_yolov4(CamStreamTriton):

    while True:
        frame = CamStreamTriton.queue.get()

        input_image_buffer = preprocess(frame, [608, 608])
        input_image_buffer = np.expand_dims(input_image_buffer, axis=0)
        CamStreamTriton.inputs[0].set_data_from_numpy(input_image_buffer)

        results = CamStreamTriton.triton_client.infer(model_name='yolov4', inputs=CamStreamTriton.inputs, outputs=CamStreamTriton.outputs, client_timeout=None)
        result = results.as_numpy('detections')

        detected_objects = postprocess(result, frame.shape[1], frame.shape[0], [608, 608], 0.8, 0.5)

        for box in detected_objects:
            frame = render_box(frame, box.box(), color=tuple(RAND_COLORS[box.classID % 64].tolist()))
            size = get_text_size(frame, f"{COCOLabels(box.classID).name}: {box.confidence:.2f}", normalised_scaling=0.6)
            frame = render_filled_box(frame, (box.x1 - 3, box.y1 - 3, box.x1 + size[0], box.y1 + size[1]), color=(220, 220, 220))
            frame = render_text(frame, f"{COCOLabels(box.classID).name}: {box.confidence:.2f}", (box.x1, box.y1), color=(30, 30, 30), normalised_scaling=0.5)
        
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


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
