from scp import user
from kantex.md import KanTeXDocument, Section, Italic, Mention


@user.on_message(
    user.me & user.command('scp')
)
async def _(_, message: user.types.Message):
    text = KanTeXDocument(
        Section('SCP-5170',
                Italic('Version'),
                Mention('TG-UserX', 777000)))
    await message.reply(text)

