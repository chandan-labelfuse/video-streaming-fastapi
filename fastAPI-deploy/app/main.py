import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env.config"))

if os.environ["DEVELOPMENT_CONFIG"] == "TEST":
    load_dotenv(os.path.join(BASE_DIR, ".env.test"))

if os.environ["DEVELOPMENT_CONFIG"] == "DOCKER":
    load_dotenv(os.path.join(BASE_DIR, ".env.docker"))

import uvicorn
from fastapi import Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates


from app import app
from db.models import Video as ModelVideo
from utils.utils import CamStreamTriton, find_camera, gen_frames_threading_yolov4, get_camera_list

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = {"page": "Home page"}
    return templates.TemplateResponse(
        "page.html", context={"request": request, "data": data}
    )


@app.get("/page/{page_name}", response_class=HTMLResponse)
async def page(request: Request, page_name: str):
    data = {"page": page_name}
    return templates.TemplateResponse(
        "page.html", context={"request": request, "data": data}
    )


@app.get("/form", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", context={"request": request})


@app.post("/form")
async def post_form(request: Request, vid: str = Form(...)):
    video_id = await ModelVideo.create(video=vid)
    data = {"vid_str": video_id}

    return templates.TemplateResponse(
        "form_post.html", context={"request": request, "data": data}
    )


@app.get("/delete_table")
async def delete_table():
    delete = await ModelVideo.delete_all()
    result = await ModelVideo.get_all()
    data = {"response": len(result), "delete": delete}
    return data




### Dashboard functions and routes


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    db_camera_list = await ModelVideo.get_all()
    camera_list = get_camera_list(db_camera_list)
    cam_id_list = list(range(0, len(camera_list)))
    context = {"request": request, "data": cam_id_list}
    return templates.TemplateResponse("dashboard.html", context=context)


@app.get("/dashboard/{video_id}")
async def video_feed(video_id: int):
    db_camera_list = await ModelVideo.get_all()
    cam = find_camera(video_id, db_camera_list)

    ## non threaded stream
    # return StreamingResponse(gen_frames(cam), media_type="multipart/x-mixed-replace;boundary=frame")

    ## threaded stream Triton
    cs = CamStreamTriton(src=cam, url=os.environ["INFERENCE_GRPC_URL"])
    cs.start()
    return StreamingResponse(
        gen_frames_threading_yolov4(cs),
        media_type="multipart/x-mixed-replace;boundary=frame",
    )


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
