from scp import user
from scp.utils.SpeedTest import Speedtest


__PLUGIN__ = 'speedTest'
__DOC__ = str(
    user.md.KanTeXDocument(
        user.md.Section(
            'Test speed on speedtest.net',
            user.md.SubSection(
                'speedTest',
                user.md.Code('(*prefix)speedTest'),
            ),
        ),
    ),
)


@user.on_message(user.sudo & user.command('speedTest'))
async def _(_, message: user.types.Message):
    reply = await message.reply('`SpeedTest ...`', quote=True)
    s: Speedtest = await Speedtest()
    await s.get_best_server()
    await s.download()
    await s.upload()
    text = user.md.KanTeXDocument(
        user.md.Section(
            'speedTest',
            user.md.SubSection(
                'Ping:',
                user.md.Code(str(s.results.ping) + 'ms'),
            ),
            user.md.SubSection(
                'Download:',
                user.md.Code(
                    str(round(s.results.download/1000.0/1000.0, 2)) + 'Mbit/s',
                ),
            ),
            user.md.SubSection(
                'Upload:',
                user.md.Code(
                    str(round(s.results.upload/1000.0 / 1000.0, 2)) + 'Mbit/s',
                ),
            ),
        ),
    )
    return await reply.edit(text)
