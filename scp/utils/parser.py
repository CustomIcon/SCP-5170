from pyrogram import types
import re
from .strUtils import bool_check  # type: ignore


def HumanizeTime(seconds: int) -> str:
    count = 0
    ping_time = ''
    time_list = []
    time_suffix_list = ['s', 'm', 'h', 'days']
    while count < 4:
        count += 1
        remainder, result = divmod(
            seconds, 60,
        ) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ', '

    time_list.reverse()
    ping_time += ':'.join(time_list)
    return ping_time


def getAttr(
    message: types.Message,
    Attr: list,
):
    for attribute in Attr:
        attr = getattr(message, attribute)
        if attr:
            return attr


def checkToken(token: str) -> bool:
    token = re.findall(
        r'[0-9]{10}:[a-zA-Z0-9_-]{35}',
        token,
    )
    if len(token) == 0:
        return False, False
    else:
        return True, token[0]


def permissionParser(perms):
    text = ''
    text += 'Message: ' + bool_check(perms.can_send_messages) + '\n'
    text += 'Media: ' + bool_check(perms.can_send_media_messages) + '\n'
    text += 'Sticker: ' + bool_check(perms.can_send_stickers) + '\n'
    text += 'GIF: ' + bool_check(perms.can_send_animations) + '\n'
    text += 'Game: ' + bool_check(perms.can_send_games) + '\n'
    text += 'Inline: ' + bool_check(perms.can_use_inline_bots) + '\n'
    text += 'Web: ' + bool_check(perms.can_add_web_page_previews) + '\n'
    text += 'Poll: ' + bool_check(perms.can_send_polls) + '\n'
    text += 'Info: ' + bool_check(perms.can_change_info) + '\n'
    text += 'invite: ' + bool_check(perms.can_invite_users) + '\n'
    text += 'Pin: ' + bool_check(perms.can_pin_messages) + '\n'
    return text
