from scp import user, bot
from scp.utils.spamCheck import is_flood, cleaner
from scp.utils.selfInfo import info
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


def _parseReport(report: str):
    tmp = {
        'abuse': user.raw.types.InputReportReasonChildAbuse(),
        'copyright': user.raw.types.InputReportReasonCopyright(),
        'fake': user.raw.types.InputReportReasonFake(),
        'porn': user.raw.types.InputReportReasonPornography(),
        'spam': user.raw.types.InputReportReasonSpam(),
        'violance': user.raw.types.InputReportReasonViolence(),
    }
    try:
        return tmp[report]
    except KeyError:
        return tmp['spam']


@user.on_message(
    user.filters.group
    & user.filters.reply
    & (
        user.filters.regex(r'(?i)@admin(s)?')
        | user.command('report', prefixes='/')
    ),
)
async def _(_, message: user.types.Message):
    """
    a function to log admin calls
    """
    uid = message.from_user.id if message.from_user else message.sender_chat.id
    url = message.reply_to_message.link
    msg = message.reply_to_message.message_id
    cht = message.chat.id
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
            [
                [
                    user.types.InlineKeyboardButton(
                        'message.link',
                        url=url,
                    ),
                ],
                [
                    user.types.InlineKeyboardButton(
                        'Abuse',
                        callback_data=f'report_{cht}_{msg}_abuse',
                    ),
                    user.types.InlineKeyboardButton(
                        'Copyright',
                        callback_data=f'report_{cht}_{msg}_copyright',
                    ),
                ],
                [
                    user.types.InlineKeyboardButton(
                        'Fake',
                        callback_data=f'report_{cht}_{msg}_fake',
                    ),
                    user.types.InlineKeyboardButton(
                        'Porn',
                        callback_data=f'report_{cht}_{msg}_porn',
                    ),
                ],
                [
                    user.types.InlineKeyboardButton(
                        'Spam',
                        callback_data=f'report_{cht}_{msg}_spam',
                    ),
                    user.types.InlineKeyboardButton(
                        'Violance',
                        callback_data=f'report_{cht}_{msg}_violance',
                    ),
                ],
            ],
        ),
    )


@bot.on_callback_query(
    (bot.sudo | bot.filters.user(info['_user_id']))
    & bot.filters.regex('^report_'),
)
async def _(_, query: user.types.CallbackQuery):
    data = query.data.split('_')
    uid = data[1]
    message_id = data[2]
    reason = data[3]
    await user.send(
        user.raw.functions.messages.Report(
            peer=await user.resolve_peer(int(uid)),
            id=[int(message_id)],
            reason=_parseReport(reason),
            message=reason,
        ),
    )
    await query.edit_message_reply_markup(
        reply_markup=user.types.InlineKeyboardMarkup(
            [[
                user.types.InlineKeyboardButton(
                    'message.link',
                    url='https://t.me/c/{}/{}'.format(
                        uid.replace('-100', ''),
                        message_id,
                    ),
                ),
            ]],
        ),
    )


asyncio.create_task(cleaner())
