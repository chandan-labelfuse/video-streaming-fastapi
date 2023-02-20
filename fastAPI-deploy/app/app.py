from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from db.database import SessionLocal, engine
from db import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")