from scp import user, __version__, bot, RUNTIME, __longVersion__
import time
from scp.utils.parser import HumanizeTime
from scp.utils.selfInfo import info
from scp.utils.unpack import unpackInlineMessage


@user.on_message(
    user.sudo & user.command('scp'),
)
async def _(_, message: user.types.Message):
    x = await user.get_inline_bot_results(info['_bot_username'], 'scp')
    for m in x.results:
        await message.reply_inline_bot_result(x.query_id, m.id, quote=True)


@bot.on_inline_query(
    bot.filters.user(info['_user_id'])
    & bot.filters.regex('^scp'),
)
async def _(_, query: bot.types.InlineQuery):
    start = time.time()
    m = await user.send_message('me', '.')
    end = time.time()
    await m.delete()
    with user.storage.lock, user.storage.conn:
        groups = user.storage.conn.execute(
            'SELECT id FROM peers WHERE type in '
            '("group", "supergroup", "channel")',
        ).fetchall()
        users = user.storage.conn.execute(
            'SELECT id FROM peers WHERE type in ("user", "bot")',
        ).fetchall()
    text = user.md.KanTeXDocument(
        user.md.Section(
            'SCP-5170',
            user.md.SubSection(
                'version: {}'.format(
                    user.md.Link(
                        __version__,
                        'https://github.com/pokurt/SCP-5170/commit/{}'.format(
                            __longVersion__,
                        ),
                    ),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('dc_id'),
                    user.md.Code(await user.storage.dc_id()),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('ping_dc'),
                    user.md.Code(f'{round((end - start) * 1000, 3)}ms'),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('peer_users'),
                    user.md.Code(f'{len(users)} users'),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('peer_groups'),
                    user.md.Code(f'{len(groups)} groups'),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('scp_uptime'),
                    user.md.Code(HumanizeTime(time.time() - RUNTIME)),
                ),
            ),
        ),
    )
    await query.answer(
        results=[
            bot.types.InlineQueryResultArticle(
                title='SCP-5170',
                description=__version__,
                input_message_content=bot.types.InputTextMessageContent(
                    text,
                    disable_web_page_preview=True,
                ),
                reply_markup=bot.types.InlineKeyboardMarkup(
                    [[
                        bot.types.InlineKeyboardButton(
                            'Source', url='https://github.com/pokurt/SCP-5170',
                        ),
                        bot.types.InlineKeyboardButton(
                            'close', callback_data='close_message',
                        ),
                    ]],
                ),
            ),
        ],
        cache_time=0,
    )


@bot.on_callback_query(
    (bot.sudo | bot.filters.user(info['_user_id']))
    & bot.filters.regex('^close_message'),
)
async def _(_, query: user.types.CallbackQuery):
    unPacked = unpackInlineMessage(query.inline_message_id)
    await user.delete_messages(
        chat_id=unPacked.chat_id,
        message_ids=unPacked.message_id,
    )
