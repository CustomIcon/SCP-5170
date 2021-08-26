from scp import user, bot
from scp.utils.spamCheck import is_flood, cleaner
import asyncio


@user.on_message(
    ~user.filters.bot &
    ~user.sudo &
    ~user.filters.chat(
        [int(i) for i in user._config.get('scp-5170', 'IgnoreGroups').split()],
    )
    & user.filters.group,
)
async def _(_, message: user.types.Message):
    """
    a function to log Spam Detection
    """
    uid = message.from_user or message.sender_chat
    if await is_flood(uid) and await user.send(
        user.raw.functions.messages.ReportSpam(
            peer=await user.resolve_peer(uid.id),
        ),
    ):
        return await bot.send_message(
            user.log_channel,
            user.md.KanTeXDocument(
                user.md.Section(
                    '#SpamDetect',
                    user.md.SubSection(
                        message.chat.title,
                        user.md.KeyValueItem(
                            user.md.Bold('chat_id'), user.md.Code(
                                message.chat.id,
                            ),
                        ),
                        user.md.KeyValueItem(
                            user.md.Bold(
                                'user_id',
                            ), user.md.Code(uid.id),
                        ),
                        user.md.KeyValueItem(
                            user.md.Bold('message_id'), user.md.Code(
                                message.message_id,
                            ),
                        ),
                    ),
                ),
            ),
            reply_markup=user.types.InlineKeyboardMarkup(
                [[
                    user.types.InlineKeyboardButton(
                        'message.link', url=message.link,
                    ),
                ]],
            ),
        )


@user.on_message(
    user.filters.group
    & user.filters.reply
    & (user.filters.regex(r'@(a|A)dmins') | user.command('report')),
)
async def _(_, message: user.types.Message):
    """
    [WIP] a function to log admin calls
    """
    uid = message.from_user.id if message.from_user else message.sender_chat.id
    url = message.reply_to_message.link
    return await bot.send_message(
        user.log_channel,
        user.md.KanTeXDocument(
            user.md.Section(
                '#Report',
                user.md.SubSection(
                    message.chat.title,
                    user.md.KeyValueItem(
                        user.md.Bold('chat_id'), user.md.Code(
                            message.chat.id,
                        ),
                    ),
                    user.md.KeyValueItem(
                        user.md.Bold(
                            'user_id',
                        ), user.md.Code(uid),
                    ),
                    user.md.KeyValueItem(
                        user.md.Bold('message_id'), user.md.Code(
                            message.message_id,
                        ),
                    ),
                ),
            ),
        ),
        reply_markup=user.types.InlineKeyboardMarkup(
            [[
                user.types.InlineKeyboardButton(
                    'message.link',
                    url=url,
                ),
            ]],
        ),
    )


asyncio.create_task(cleaner())
