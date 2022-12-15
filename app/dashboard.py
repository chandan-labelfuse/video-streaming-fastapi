# from fastapi import APIRouter, Request
# from fastapi.responses import HTMLResponse, StreamingResponse
# from fastapi.templating import Jinja2Templates

# from models import Video as ModelVideo
# from schema import Video as SchemaVideo

# import cv2


# router = APIRouter()
# templates = Jinja2Templates(directory="templates")

# def get_camera_list(db_camera_list):
#     camera_list = []
#     for c in db_camera_list:
#         camera_list.append(tuple(c.values())[1])

#     if len(camera_list) > 0:
#         return camera_list
#     return []

# def find_camera(camera_id, db_camera_list):
#     camera_list = []
#     for c in db_camera_list:
#         camera_list.append(tuple(c.values())[1])

#     if len(camera_list) > 0:
#         return camera_list[camera_id]
#     return []


# def gen_frames(camera_id, db_camera_list):

#     cam = find_camera(camera_id, db_camera_list)
#     cap = cv2.VideoCapture(cam)

#     while True:

#         success, frame = cap.read()
#         if not success:
#             break
#         else:
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @router.get("/dashboard", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     db_camera_list = await ModelVideo.get_all()
#     camera_list = get_camera_list(db_camera_list)
#     context = {
#         "request": request,
#         "data": camera_list
#     }
#     return templates.TemplateResponse("dashboard.html", context=context)

# @router.get("/dashboard/video_feed/{video_id}")
# async def video_feed(video_id: int):
#     print (video_id)
#     db_camera_list = await ModelVideo.get_all()
#     return StreamingResponse(gen_frames(video_id, db_camera_list), media_type="multipart/x-mixed-replace;boundary=frame")
