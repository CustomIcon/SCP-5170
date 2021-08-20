from scp import user
import aiofiles
import os


__PLUGIN__ = 'paste'
__DOC__ = str(user.md.KanTeXDocument(
    user.md.Section('Paste Utility',
        user.md.SubSection('paste',
            user.md.Code('(*prefix)paste {content}')))))


@user.on_message(user.sudo & user.command("paste"))
async def _(_, message: user.types.Message):
    if len(message.command) != 1:
        text = message.text.split(None, 1)[1]
    else:
        text = None
    if message.reply_to_message:
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        elif (
            message.reply_to_message.document
            and message.reply_to_message.document.file_size < 2 ** 20 * 10
        ):
            path = await message.reply_to_message.download()
            async with aiofiles.open(path, 'r') as doc:
                text = await doc.read()
                await doc.close()
            os.remove(path)
    if not text:
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