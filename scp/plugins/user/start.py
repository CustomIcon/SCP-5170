from scp import user, __version__

__PLUGIN__ = 'start'


@user.on_message(
    user.filters.me & user.command('scp')
)
async def _(_, message: user.types.Message):
    text = user.md.KanTeXDocument(
        user.md.Section('SCP-5170',
                user.md.KeyValueItem(key='Version', value=__version__),
                user.md.Link(label='SCP-Foundation', url='https://scp-wiki.wikidot.com/')))
    await message.reply(text, quote=True, disable_web_page_preview=True)

