from scp import bot, user, __version__
from scp.utils.selfInfo import info


@bot.on_message(
    (bot.sudo | bot.filters.user(info['_user_id']))
    & bot.command('start', prefixes='/'),
)
async def _(_, message: bot.types.Message):
    try:
        me = await user.get_me()
    except ConnectionError:
        me = None
    userbot_stat = 'Stopped' if not me else 'Running'
    text = user.md.KanTeXDocument(
        user.md.Section(
            'SCP-5170',
            user.md.KeyValueItem(
                user.md.Bold('Userbot Status'), user.md.Code(userbot_stat),
            ),
            user.md.KeyValueItem(
                user.md.Bold('Version'), user.md.Code(__version__),
            ),
        ),
    )
    await message.reply(
        text,
        reply_markup=bot.types.InlineKeyboardMarkup(
            [[
                bot.types.InlineKeyboardButton(
                    'help', callback_data='help_back',
                ),
            ]],
        ),
    )
