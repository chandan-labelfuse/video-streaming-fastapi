import tritonclient.grpc as grpcclient
# import cv2
# import numpy as np

# from yolov4_processing import preprocess, postprocess
# from labels import COCOLabels
# from render import render_box, render_filled_box, get_text_size, render_text, RAND_COLORS

# url = 'localhost:8001'


def create_client(url):
	triton_client = grpcclient.InferenceServerClient(url)

	# Health check
	if not triton_client.is_server_live():
		print("FAILED : is_server_live")
		sys.exit(1)

	if not triton_client.is_server_ready():
		print("FAILED : is_server_ready")
		sys.exit(1)

	if not triton_client.is_model_ready('yolov4'):
		print("FAILED : is_model_ready")
		sys.exit(1)

	return triton_client

# triton_client = create_client(url)

# inputs = []
# outputs = []

# inputs.append(grpcclient.InferInput('input', [1, 3, 608, 608], "FP32"))
# outputs.append(grpcclient.InferRequestedOutput('detections'))

# cap = cv2.VideoCapture('http://pendelcam.kip.uni-heidelberg.de/mjpg/video.mjpg')

# while True:
# 	ret, frame = cap.read()
# 	if not ret:
# 		print("failed to fetch next frame")
# 		break

# 	input_image_buffer = preprocess(frame, [608, 608])
# 	input_image_buffer = np.expand_dims(input_image_buffer, axis=0)

# 	inputs[0].set_data_from_numpy(input_image_buffer)

# 	results = triton_client.infer(model_name='yolov4', inputs=inputs, outputs=outputs, client_timeout=None)

# 	result = results.as_numpy('detections')

# 	detected_objects = postprocess(result, frame.shape[1], frame.shape[0], [608, 608], 0.8, 0.5)


# 	for box in detected_objects:
# 		frame = render_box(frame, box.box(), color=tuple(RAND_COLORS[box.classID % 64].tolist()))
# 		size = get_text_size(frame, f"{COCOLabels(box.classID).name}: {box.confidence:.2f}", normalised_scaling=0.6)
# 		frame = render_filled_box(frame, (box.x1 - 3, box.y1 - 3, box.x1 + size[0], box.y1 + size[1]), color=(220, 220, 220))
# 		frame = render_text(frame, f"{COCOLabels(box.classID).name}: {box.confidence:.2f}", (box.x1, box.y1), color=(30, 30, 30), normalised_scaling=0.5)

# 	cv2.imshow('image', frame)
# 	if cv2.waitKey(1) == ord('q'):
# 		break