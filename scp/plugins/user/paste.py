from scp import user
import aiofiles
import os


__PLUGIN__ = 'paste'
__DOC__ = str(user.md.KanTeXDocument(
    user.md.Section('Paste Utility',
        user.md.SubSection('paste',
            user.md.Code('(*prefix)paste {content}')))))


@user.on_message(user.filters.me & user.command("paste"))
async def _(_, message: user.types.Message):
    if message.reply_to_message:
        text = message.reply_to_message.text
    if (
        message.reply_to_message.document
        and message.reply_to_message.document.file_size < 2 ** 20 * 10
    ):
        path = await message.reply_to_message.download()
        async with aiofiles.open(path, 'r') as doc:
            text = await doc.read()
            await doc.close()
        os.remove(path)
    else:
        return await message.reply(
            user.md.KanTeXDocument(
                user.md.Section('Error',
                    user.md.Italic('Paste Failed'))),
            quote=True
        )
    await message.reply(
        user.md.KanTeXDocument(
            user.md.Section('Paste',
                user.md.KeyValueItem(
                    user.md.Bold('Link'),
                    await user.netcat('termbin.com', 9999, text)))),
        quote=True
    )