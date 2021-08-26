import base64
import struct
from attrify import Attrify as Atr


def unpackInlineMessage(inline_message_id: str):
    temp = {}
    dc_id, message_id, chat_id, query_id = struct.unpack(
        '<iiiq',
        base64.urlsafe_b64decode(
            inline_message_id + '=' * (len(inline_message_id) % 4),
        ),
    )
    temp['dc_id'] = dc_id
    temp['message_id'] = message_id
    temp['chat_id'] = int(str(chat_id).replace('-1', '-100'))
    temp['query_id'] = query_id
    temp['inline_message_id'] = inline_message_id
    return Atr(temp)
