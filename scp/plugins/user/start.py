from scp import user, __version__, bot, RUNTIME
import time
from scp.utils.parser import get_readable_time
from scp.utils.selfInfo import info


@user.on_message(
    user.sudo & user.command('scp')
)
async def _(_, message: user.types.Message):
    x = await user.get_inline_bot_results(info['_bot_username'], 'scp')
    for m in x.results:
        await message.reply_inline_bot_result(x.query_id, m.id, quote=True)


@bot.on_inline_query(bot.filters.user(info['_user_id']) & bot.filters.regex('^scp'))
async def _(_, query: bot.types.InlineQuery):
    start = time.time()
    m = await user.send_message("me", '.')
    end = time.time()
    await m.delete()
    with user.storage.lock, user.storage.conn:
        groups = user.storage.conn.execute(
            'SELECT id FROM peers WHERE type in ("group", "supergroup", "channel")'
        ).fetchall()
        users = user.storage.conn.execute(
            'SELECT id FROM peers WHERE type in ("user", "bot")'
        ).fetchall()
    text = user.md.KanTeXDocument(
        user.md.Section('SCP-5170',
            user.md.SubSection(f'version: {__version__}',
                user.md.KeyValueItem(
                    user.md.Bold('dc_id'),
                    user.md.Code(await user.storage.dc_id())),
                user.md.KeyValueItem(
                    user.md.Bold('ping_dc'),
                    user.md.Code(f'{round((end - start) * 1000, 3)}ms')),
                user.md.KeyValueItem(
                    user.md.Bold('peer_users'),
                    user.md.Code(f'{len(users)} users')),
                user.md.KeyValueItem(
                    user.md.Bold('peer_groups'),
                    user.md.Code(f'{len(groups)} groups')),
                user.md.KeyValueItem(
                    user.md.Bold('scp_uptime'),
                    user.md.Code(get_readable_time(time.time() - RUNTIME))))))
    await query.answer(
        results=[
            bot.types.InlineQueryResultArticle(
                title='SCP-5170',
                description=__version__,
                input_message_content=bot.types.InputTextMessageContent(text),
                reply_markup=bot.types.InlineKeyboardMarkup(
                    [[bot.types.InlineKeyboardButton('Source', url='https://github.com/pokurt/SCP-5170')]]
                )
            )
        ],
        cache_time=0
    )