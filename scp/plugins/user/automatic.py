from scp import user, bot
from scp.utils.spamCheck import is_flood, cleaner
import asyncio


@user.on_message(
    ~user.filters.bot &
    ~user.sudo &
    ~user.filters.chat(
        [int(i) for i in user._config.get('scp-5170', 'IgnoreGroups').split()]
    )
    & user.filters.group
)
async def _(_, message: user.types.Message):
    """
    a function to log Spam Detection
    """
    if message.from_user:
        uid = message.from_user
    else:
        uid = message.sender_chat
    if await is_flood(uid):
        return await bot.send_message(
            user.log_channel,
            user.md.KanTeXDocument(
                user.md.Section('#SpamDetect',
                    user.md.SubSection(message.chat.title,
                        user.md.KeyValueItem(
                            user.md.Bold('chat_id'), user.md.Code(message.chat.id)
                        ),
                        user.md.KeyValueItem(
                            user.md.Bold('user_id'), user.md.Code(uid.id)
                        ),
                        user.md.KeyValueItem(
                            user.md.Bold('message_id'), user.md.Code(message.message_id))
                        )
                    )
            ),
            reply_markup=user.types.InlineKeyboardMarkup(
                [[user.types.InlineKeyboardButton('message.link', url=message.link)]]
            )
        )


@user.on_message(
    user.filters.group
    & (user.filters.regex(r'@(a|A)dmins') | user.command('report'))
)
async def _(_, message: user.types.Message):
    """
    [WIP] a function to log admin calls
    """
    if message.from_user:
        uid = message.from_user.id
    else:
        uid = message.sender_chat.id
    return await bot.send_message(
        user.log_channel,
        user.md.KanTeXDocument(
            user.md.Section('#Report',
                user.md.SubSection(message.chat.title,
                    user.md.KeyValueItem(
                        user.md.Bold('chat_id'), user.md.Code(message.chat.id)
                    ),
                    user.md.KeyValueItem(
                        user.md.Bold('user_id'), user.md.Code(uid)
                    ),
                    user.md.KeyValueItem(
                        user.md.Bold('message_id'), user.md.Code(message.message_id))
                    )
                )
        ),
        reply_markup=user.types.InlineKeyboardMarkup(
            [[user.types.InlineKeyboardButton(
                'message.link',
                url=message.reply_to_message.link if message.reply_to_message else message.link)]]
        )
    )


asyncio.create_task(cleaner())