from peewee import *
from mpd_radioalarm.plugins import PluginBase


class BroadcastTransmitter(PluginBase.model.BaseModel):
    url = CharField()
    name = CharField(unique=True)


class MP3File(PluginBase.model.BaseModel):
    file = CharField(unique=True)
    title = CharField()
    artist = CharField()
    album = CharField()
    year = IntegerField()
    comment = CharField()
    genre = CharField()


class Alarm(PluginBase.model.BaseModel):
    mins = IntegerField()
    secs = IntegerField()
    hours = IntegerField()
    days = IntegerField()
    weekdays = IntegerField()
    year = IntegerField()
    name = CharField()
    mp3file = ForeignKeyField(MP3File)
    broadcasttransmitter = ForeignKeyField(BroadcastTransmitter)

