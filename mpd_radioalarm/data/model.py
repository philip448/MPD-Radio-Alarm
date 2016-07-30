from peewee import *
from mpd_radioalarm import config
from uuid import uuid4

db = SqliteDatabase(config.DATABASE_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    password = CharField()
    email = CharField(unique=True)


class Session(BaseModel):
    token = UUIDField(default=lambda: str(uuid4()))
    user = ForeignKeyField(User, related_name='sessions')

db.connect()
db.create_tables([
    User,
    Session
], safe=True)

