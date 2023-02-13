from db.db import db, metadata, sqlalchemy

videos = sqlalchemy.Table(
    "videos",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("video", sqlalchemy.String),
)


class Video:
    @classmethod
    async def get(cls, id):
        query = videos.select().where(videos.c.id == id)
        video = await db.fetch_one(query)
        return video

    @classmethod
    async def create(cls, **video):
        query = videos.insert().values(**video)
        video_id = await db.execute(query)
        return video_id

    @classmethod
    async def get_all(cls):
        query = videos.select()
        video_list = await db.fetch_all(query)
        return video_list

    @classmethod
    async def delete_all(cls):
        query = videos.delete()
        await db.execute(query)
        return "Deleted all rows"
