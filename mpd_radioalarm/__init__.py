import hashlib

from mpd_radioalarm import config


def password(plain):
    if not config.HASH_PASSWORD:
        return plain
    return str(hashlib.pbkdf2_hmac(config.HASH_ALGO, str.encode(plain),
                                   str.encode(config.HASH_SALT),
                                   config.HASH_ITERATIONS))

# https://gist.github.com/smoak/1045874
class EventHook(object):
  def __init__(self):
    self.__handlers = []

  def addHandler(self, handler):
    self.__handlers.append(handler)

  def removeHandler(self, handler):
    self.__handlers.remove(handler)

  def fire(self, *args, **kwargs):
    for handler in self.__handlers:
      handler(*args, **kwargs)

  def clearObjectHandlers(self, inObject):
    for theHandler in self.__handlers:
      if theHandler.im_self == inObject:
        self.removeHandler(theHandler)