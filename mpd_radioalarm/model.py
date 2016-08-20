from peewee import *
from mpd_radioalarm import config
from uuid import uuid4
_db = SqliteDatabase(config.DATABASE_PATH)


def create_table(model_class, safe=True):
    _db.create_table(model_class, safe)


class BaseModel(Model):
    class Meta:
        database = _db


class User(BaseModel):
    password = CharField()
    email = CharField(unique=True)
    uuid = UUIDField(default=lambda: str(uuid4()))


class Session(BaseModel):
    token = UUIDField(default=lambda: str(uuid4()))
    user = ForeignKeyField(User, related_name='sessions')


class Group(BaseModel):
    name = CharField(unique=True)
    uuid = UUIDField(default=lambda: str(uuid4()))


class UserGroup(BaseModel):
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)




_db.connect()
_db.create_tables([
    User,
    Session,
    Group,
    UserGroup
], safe=True)

