from scp.utils.selfInfo import info
from scp import bot


@bot.on_message(
    bot.filters.user(info['_user_id'])
    & bot.command('config', prefixes='/')
    & bot.filters.private,
)
async def _(_, message: bot.types.Message):
    doc = bot.md.KanTeXDocument()
    sec = bot.md.Section('Configurations')
    for x, y in bot._config.__dict__['_sections'].items():
        subsec = bot.md.SubSection(x)
        for i, n in y.items():
            conf = bot.md.KeyValueItem(bot.md.Bold(i), bot.md.Code(n))
            subsec.append(conf)
        sec.append(subsec)
    doc.append(sec)
    await message.reply(
        doc,
        reply_markup=bot.types.InlineKeyboardMarkup(
            [[
                bot.types.InlineKeyboardButton(
                    'Edit Config', callback_data='edit/config',
                ),
            ]],
        ),
    )


@bot.on_callback_query(
    bot.filters.user(
        info['_user_id'],
    )
    & bot.filters.regex('^edit/config'),
)
async def _(_, query: bot.types.CallbackQuery):
    if query.data == 'edit/config':
        buttons = []
        for _, y in bot._config.__dict__['_sections'].items():
            for i in y:
                buttons.append(
                    [
                        bot.types.InlineKeyboardButton(
                            i, callback_data=f'edit/config/{i}',
                        ),
                    ],
                )
        return await query.edit_message_text(
            'choose a config key to edit in config.ini',
            reply_markup=bot.types.InlineKeyboardMarkup(buttons),
        )
    toEdit = query.data.split('/')[2]
    for x, y in bot._config.__dict__['_sections'].items():
        for i, n in y.items():
            if i == toEdit:
                await query.edit_message_text(
                    bot.md.KanTeXDocument(
                        bot.md.Section(
                            'EditConfig current key and value',
                            bot.md.KeyValueItem(
                                bot.md.Bold(i),
                                bot.md.Code(n),
                            ),
                        ),
                    ),
                )
                editConfig = await query.from_user.ask(
                    f'send me the value to change in {i}',
                )
                bot._config.set(x, i, editConfig.text)
                with open('config.ini', 'w') as configfile:
                    bot._config.write(configfile)
                return await query.message.reply(
                    bot.md.KanTeXDocument(
                        bot.md.Section(
                            'Success',
                            bot.md.SubSection(
                                'Changes:',
                                bot.md.KeyValueItem(
                                    bot.md.Bold(
                                        i,
                                    ), bot.md.Code(editConfig.text),
                                ),
                            ),
                        ),
                    ),
                )
