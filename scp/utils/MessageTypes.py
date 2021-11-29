from enum import IntEnum, unique
from scp import user
from scp.utils.parser import getAttr


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
    data_type = None
    content = None
    m = getAttr(message, ['reply_to_message']) or message
    try:
        content = m.text
    except AttributeError:
        content = None
    data_type = Types.TEXT
    if m.sticker:
        content = m.sticker.file_id
        data_type = Types.STICKER
    elif m.document:
        content = m.document.file_id
        data_type = Types.DOCUMENT
    elif m.photo:
        content = m.photo.file_id
        data_type = Types.PHOTO
    elif m.audio:
        content = m.audio.file_id
        data_type = Types.AUDIO
    elif m.voice:
        content = m.voice.file_id
        data_type = Types.VOICE
    elif m.video:
        content = m.video.file_id
        data_type = Types.VIDEO
    return data_type, content, message.caption
