from queue import Queue
from threading import Thread
from dataclasses import dataclass, field
from typing import List, Any, Generator

import cv2
import numpy as np
from PIL import Image
import tritonclient.grpc as grpcclient

from components.abscomp import CamObject, DetectorObject, DrawObject, ControllerObject
from components.utils import create_client
from components.yolov4.processing import preprocess, postprocess
from components.yolov4.render import render_box, render_filled_box, get_text_size, render_text, RAND_COLORS
from components.yolov4.labels import COCOLabels


class CVCam(CamObject):

	def initialize(self) -> None:
		self.stream = cv2.VideoCapture(self.cam_address)
		(self.grabbed, self.frame) = self.stream.read()

		self.h, self.w, self.c = self.frame.shape		

		self.stopped = False

		self.queue = Queue(120)

		self.t = Thread(target=self.update, args=())
		self.t.daemon = True
	
	def start(self) -> None:
		self.stopped = False
		self.t.start()

	def update(self) -> None:
		while True:
			if self.stopped:
				break
			(self.grabbed, self.frame) = self.stream.read()
			self.queue.put(self.frame)

	def read(self) -> np.ndarray:
		return self.frame

	def stop(self) -> None:
		self.stopped = True
		self.stream.release()


@dataclass
class TritonYolov4Detector(DetectorObject):

	url: str
	inputs: List[Any] = field(default_factory=list)
	outputs: List[Any] = field(default_factory=list)

	def initialize(self) -> None:
		self.triton_client = create_client(url=self.url)
		self.inputs.append(grpcclient.InferInput('input', [1, 3, 608, 608], "FP32"))
		self.outputs.append(grpcclient.InferRequestedOutput('detections'))

	def preprocess(self, img: np.ndarray) -> None:
		input_image_buffer = preprocess(img, [608, 608])
		input_image_buffer = np.expand_dims(input_image_buffer, axis=0)
		self.inputs[0].set_data_from_numpy(input_image_buffer)

	def infer(self) -> Any:
		return self.triton_client.infer(model_name='yolov4', inputs=self.inputs, outputs=self.outputs, client_timeout=None)

	def postprocess(self, prediction: Any) -> List:
		result = prediction.as_numpy('detections')
		detected_objects = postprocess(result, self.cam.w, self.cam.h, [608, 608], 0.8, 0.5)
		return detected_objects
	

class TritonYolov4Draw(DrawObject):
	def draw(self, image: np.ndarray, detections: List) -> np.ndarray:
		for box in detections:
			frame = render_box(image, box.box(), color=tuple(RAND_COLORS[box.classID % 64].tolist()))
			size = get_text_size(frame, f"{COCOLabels(box.classID).name}: {box.confidence:.2f}", normalised_scaling=0.6)
			frame = render_filled_box(frame, (box.x1 - 3, box.y1 - 3, box.x1 + size[0], box.y1 + size[1]), color=(220, 220, 220))
			frame = render_text(frame, f"{COCOLabels(box.classID).name}: {box.confidence:.2f}", (box.x1, box.y1), color=(30, 30, 30), normalised_scaling=0.5)
		return frame


class CVRender(ControllerObject):
	def render(self) -> Generator[Any, None, None]:
		while True:
			frame = self.camComp.queue.get()

			if self.detectComp:
				preprocessed_frame = self.detectComp.preprocess(frame)
				detections = self.detectComp.infer(preprocessed_frame)
				postprocessed_object = self.detectComp.postprocess(detections)

				if self.actionComp:
					print ("action")
			
				if self.drawComp:
					frame = self.drawComp.draw(frame, postprocessed_object)
			
			ret, render = cv2.imencode(".jpg", frame)
			frame = render.tobytes()
			yield (
            	b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        	)


# cam = CVObject(1, "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4")
# predictor = TritonYolov4Object(cam, "asasa")

# predictor.initialize()