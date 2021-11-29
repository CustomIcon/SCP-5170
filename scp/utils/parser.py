from pyrogram import types
import re


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
