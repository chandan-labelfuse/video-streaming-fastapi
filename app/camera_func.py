import cv2


async def find_camera(camera_id):

	db_camera_list = await ModelVideo.get_all()
	camera_list = []
	for c in db_camera_list:
		camera_list.append(c.values[1])
	print (camera_list)


def gen_frames(camera_id):

	cam = cameras[camera_id]
	cap = cv2.VideoCapture(cam)

	while True:

		success, frame = cap.read()
		if not success:
			break
		else:
			ret, buffer = cv2.imencode('.jpg', frame)
			frame = buffer.tobytes()
			yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')