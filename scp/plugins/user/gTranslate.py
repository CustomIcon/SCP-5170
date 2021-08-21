from gpytranslate import Translator
from scp import user
import aiofiles
import os
import asyncio


__PLUGIN__ = 'translate'
__DOC__ = str(user.md.KanTeXDocument(
    user.md.Section('Google Translate',
        user.md.SubSection('translate',
            user.md.Code('(*prefix)tr {language_code} {text} - * optional'))),
        user.md.SubSection('text-to-speech',
            user.md.Code('(*prefix)tts {text}'))))


trl = Translator()


@user.on_message(user.sudo & user.command('tl'))
async def _(_, message: user.types.Message):
    if message.reply_to_message and (
        message.reply_to_message.text
        or message.reply_to_message.caption
    ):
        if len(message.text.split()) == 1:
            return await message.delete()
        target = message.text.split()[1]
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            text = message.reply_to_message.caption
        try:
            tekstr = await trl.translate(text, targetlang=target)
        except ValueError as err:
            await message.reply(
                user.md.KanTeXDocument(
                    user.md.Section('Error', user.md.Italic(str(err)))
                ), quote=True
            )
            return
    else:
        if len(message.text.split()) <= 2:
            return await message.delete()
        target = message.text.split(None, 2)[1]
        text = message.text.split(None, 2)[2]
        try:
            tekstr = await trl.translate(text, targetlang=target)
        except ValueError as err:
            return await message.reply(
                user.md.KanTeXDocument(
                    user.md.Section('Error', user.md.Italic(str(err)))
                ),
                quote=True
            )
    detect = await trl.detect(text)
    await message.reply(
        user.md.KanTeXDocument(
            user.md.Section('Translator',
                user.md.SubSection('Translated:',
                    user.md.Code(tekstr.text)),
                user.md.SubSection('Detected language:',
                    user.md.Code(detect)),)),
        quote=True
    )


@user.on_message(user.sudo & user.command('tts'))
async def _(_, message: user.types.Message):
    if len(message.command) != 1:
        text = message.text.split(None, 1)[1]
    else:
        text = None
    if message.reply_to_message:
        if message.reply_to_message.text:
            text = message.reply_to_message.text
    async with aiofiles.open("tts.mp3", "wb") as file:
        await trl.tts(text, file=file, targetlang="en")
    await message.reply_audio("tts.mp3")
    os.remove('tts.mp3')