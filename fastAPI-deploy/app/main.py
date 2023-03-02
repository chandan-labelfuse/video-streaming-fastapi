import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env.config"))

if os.environ["DEVELOPMENT_CONFIG"] == "TEST":
    load_dotenv(os.path.join(BASE_DIR, ".env.test"))

if os.environ["DEVELOPMENT_CONFIG"] == "DOCKER":
    load_dotenv(os.path.join(BASE_DIR, ".env.docker"))

import uvicorn
from fastapi import Form, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from starlette.responses import RedirectResponse, Response

from app import app
from db.schema import User
from db.deps import get_db
from utils.utils import CamStreamTriton, find_camera, gen_frames_threading_yolov4, get_camera_list
from core.auth import authenticate, create_access_token
from core.deps import get_current_user

from components.comp import CVCam, CVRender

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = {"page": "Home page"}
    return templates.TemplateResponse(
        "page.html", context={"request": request, "data": data})


### Login, Signup, Logout Routes

## Login Route
@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request})

@app.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = await authenticate(data.username, data.password, db)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        token = jsonable_encoder(create_access_token(sub=user.email))
        response = RedirectResponse(url="/", status_code = status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            "Authorization",
            value = f"Bearer {token}",
            max_age=1800,
            expires=1800,
        )

        return response
    except Exception as e:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response


@app.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    user = current_user

## Create account
@app.get("/create", response_class=HTMLResponse)
async def create(request: Request):
    return templates.TemplateResponse("request.html", context={"request": request})

## Reset account
@app.get("/reset", response_class=HTMLResponse)
async def reset(request: Request):
    return templates.TemplateResponse("passcode.html", context={"request": request})


## Logout

@app.get("/logout")
async def logout_and_remove_cookie():
    response = RedirectResponse(url="/", status_code = status.HTTP_303_SEE_OTHER)
    response.delete_cookie("Authorization")
    return response 

@app.get("/page/{page_name}", response_class=HTMLResponse)
async def page(request: Request, page_name: str):
    data = {"page": page_name}
    return templates.TemplateResponse(
        "page.html", context={"request": request, "data": data}
    )


### Dashboard functions and routes
@app.get("/demo", response_class=HTMLResponse)
async def demo(request: Request):
    return templates.TemplateResponse("demo.html", context={"request": request})

@app.get("/demo/camera")
async def demo_feed():
    cam = CVCam(1, "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4")
    render = CVRender(cam)

    cam.initialize()
    cam.start()

    return StreamingResponse(
        render.render(),
        media_type="multipart/x-mixed-replace;boundary=frame",
    )


# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     db_camera_list = await ModelVideo.get_all()
#     camera_list = get_camera_list(db_camera_list)
#     cam_id_list = list(range(0, len(camera_list)))
#     context = {"request": request, "data": cam_id_list}
#     return templates.TemplateResponse("dashboard.html", context=context)


# @app.get("/dashboard/{video_id}")
# async def video_feed(video_id: int):
#     db_camera_list = await ModelVideo.get_all()
#     cam = find_camera(video_id, db_camera_list)

#     ## non threaded stream
#     # return StreamingResponse(gen_frames(cam), media_type="multipart/x-mixed-replace;boundary=frame")

#     ## threaded stream Triton
#     cs = CamStreamTriton(src=cam, url=os.environ["INFERENCE_GRPC_URL"])
#     cs.start()
#     return StreamingResponse(
#         gen_frames_threading_yolov4(cs),
#         media_type="multipart/x-mixed-replace;boundary=frame",
#     )


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
