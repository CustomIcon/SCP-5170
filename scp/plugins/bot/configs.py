from scp.utils.selfInfo import info
from scp import bot

@bot.on_message(
    bot.filters.user(info['_user_id'])
    & bot.command('config')
    & bot.filters.private)
async def _(_, message:bot.types.Message):
    doc = bot.md.KanTeXDocument()
    sec = bot.md.Section('Configurations')
    for x, y in bot._config.__dict__['_sections'].items():
        subsec = bot.md.SubSection(x)
        for i, n in y.items():
            conf = bot.md.KeyValueItem(bot.md.Bold(i), bot.md.Code(n))
            subsec.append(conf)
        sec.append(subsec)
    doc.append(sec)
    await message.reply(doc)
