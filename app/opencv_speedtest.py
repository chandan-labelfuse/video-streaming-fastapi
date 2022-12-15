import cProfile
import time
from threading import Thread
from time import time

import cv2
import yappi

## CV2 threading
threads = []

yappi.start()


class CamStream:
    def __init__(self, src):

        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        self.stopped = False

        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        threads.append(self.t)

    def start(self):

        self.stopped = False
        self.t.start()

    def update(self):

        while True:
            if self.stopped:
                break

            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


cs = CamStream(
    src="rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4"
)
cs.start()

for i in range(0, 1000):
    frame = cs.read()
    ret, buffer = cv2.imencode(".jpg", frame)
    frame = buffer.tobytes()

cs.stopped = True
# time.sleep(0.03)
print("STOPPED")
for t in threads:
    t.join()

yappi.stop()


threads = yappi.get_thread_stats()
for thread in threads:
    print(
        "Function stats for (%s) (%d)" % (thread.name, thread.id)
    )  # it is the Thread.__class__.__name__
    yappi.get_func_stats(ctx_id=thread.id).print_all()


## CV2 normal execution
# yappi.set_clock_type("cpu")
# yappi.start()


# def gen_frames():

# 	# cam = find_camera(camera_id, db_camera_list)
# 	cap = cv2.VideoCapture('rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4')

# 	for i in range(0, 1000):

# 		success, frame = cap.read()
# 		if not success:
# 			print (success)
# 			break
# 		else:
# 			ret, buffer = cv2.imencode('.jpg', frame)
# 			frame = buffer.tobytes()
# 			# yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# gen_frames()

# yappi.get_func_stats().print_all()
# yappi.get_thread_stats().print_all()
