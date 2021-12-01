from enum import IntEnum, unique
from scp import user


@unique
class Types(IntEnum):
    TEXT = 0
    BUTTON_TEXT = 1
    STICKER = 2
    DOCUMENT = 3
    PHOTO = 4
    AUDIO = 5
    VOICE = 6
    VIDEO = 7


def getType(message: user.types.Message):
    dataType = None
    content = None
    try:
        content = message.text
    except AttributeError:
        content = None
    dataType = Types.TEXT
    if message.sticker:
        content = message.sticker.file_id
        dataType = Types.STICKER
    elif message.document:
        content = message.document.file_id
        dataType = Types.DOCUMENT
    elif message.photo:
        content = message.photo.file_id
        dataType = Types.PHOTO
    elif message.audio:
        content = message.audio.file_id
        dataType = Types.AUDIO
    elif message.voice:
        content = message.voice.file_id
        dataType = Types.VOICE
    elif message.video:
        content = message.video.file_id
        dataType = Types.VIDEO
    return dataType, content, message.caption
