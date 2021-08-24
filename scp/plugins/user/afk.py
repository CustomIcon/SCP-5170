from datetime import datetime

from scp import user, bot
from scp.utils.selfInfo import info

import humanize


AFK = False
AFK_REASON = ""
AFK_TIME = ""
USERS = {}
GROUPS = {}


def subtract_time(start, end):
    return str(humanize.naturaltime(start - end))


@user.on_message(
    ((user.filters.group & user.filters.mentioned)
    | user.filters.private)
    & ~user.filters.me 
    & ~user.filters.bot
    & ~user.filters.service,
    group=3
)
async def _(_, message: user.types.Message):
    if AFK:
        last_seen = subtract_time(datetime.now(), AFK_TIME)
        is_group = True if message.chat.type in ["supergroup", "group"] else False
        CHAT_TYPE = GROUPS if is_group else USERS

        if message.chat.id not in CHAT_TYPE:
            text = user.md.KanTeXDocument(
                user.md.Section('Away from Keyboard',
                    user.md.KeyValueItem(user.md.Bold('last_seen'), user.md.Code(last_seen)),
                    user.md.KeyValueItem(user.md.Bold('reason'), user.md.Code(AFK_REASON))))
            CHAT_TYPE[message.chat.id] = 1
            return await user.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_to_message_id=message.message_id,
            )
        elif message.chat.id in CHAT_TYPE:
            if CHAT_TYPE[message.chat.id] == 50:
                text = user.md.KanTeXDocument(
                    user.md.Section('Away from Keyboard',
                        user.md.KeyValueItem(
                            user.md.Bold('last_seen'), user.md.Code(last_seen)
                        )
                    )
                )
                await user.send_message(
                    chat_id=message.chat.id,
                    text=text,
                    reply_to_message_id=message.message_id,
                )
            elif CHAT_TYPE[message.chat.id] > 50:
                return
            elif CHAT_TYPE[message.chat.id] % 5 == 0:
                text = user.md.KanTeXDocument(
                    user.md.Section('Away from Keyboard',
                        user.md.KeyValueItem(user.md.Bold('last_seen'), user.md.Code(last_seen)),
                        user.md.KeyValueItem(user.md.Bold('reason'), user.md.Code(AFK_REASON))))
                await user.send_message(
                    chat_id=message.chat.id,
                    text=text,
                    reply_to_message_id=message.message_id,
                )

        CHAT_TYPE[message.chat.id] += 1


@user.on_message(user.command("afk") & user.filters.me, group=3)
async def _(_, message: user.types.Message):
    global AFK_REASON, AFK, AFK_TIME
    cmd = message.command
    afk_text = ""
    if len(cmd) > 1:
        afk_text = " ".join(cmd[1:])
    if isinstance(afk_text, str):
        AFK_REASON = afk_text
    AFK = True
    AFK_TIME = datetime.now()
    await message.delete()


@user.on_message(user.filters.me, group=3)
async def _(_, __):
    global AFK, AFK_TIME, AFK_REASON, USERS, GROUPS
    if AFK:
        last_seen = subtract_time(datetime.now(), AFK_TIME).replace("ago", "").strip()
        await bot.send_message(
            info['_user_id'],
            f"While you were away (for {last_seen}), you received {sum(USERS.values()) + sum(GROUPS.values())} "
            f"messages from {len(USERS) + len(GROUPS)} chats`"
        )
        AFK = False
        AFK_TIME = ""
        AFK_REASON = ""
        USERS = {}
        GROUPS = {}