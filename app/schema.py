from pydantic import BaseModel


class Video(BaseModel):
    video: str

    class Config:
        orm_mode = True
