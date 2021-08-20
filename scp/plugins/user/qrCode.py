from scp import user
from pyzxing import BarCodeReader
from io import BytesIO
import os
from pyrogram import errors


__PLUGIN__ = 'qrCode'
__DOC__ = str(user.md.KanTeXDocument(
    user.md.Section('Qrcode Encoding & Decoding',
        user.md.SubSection('Encode',
            user.md.Code('(*prefix)qrGen {content}')),
        user.md.SubSection('Decode',
            user.md.Code('(*prefix)qrRead {replied_media}')))))


def _gen(content: str):
    return {
    "data":content,
    "config":{
        "body":"circle-zebra",
        "eye":"frame13",
        "eyeBall":"ball14",
        "erf1":[],
        "erf2":[],
        "erf3":[],
        "brf1":[],
        "brf2":[],
        "brf3":[],
        "bodyColor":"#000000",
        "bgColor":"#FFFFFF",
        "eye1Color":"#000000",
        "eye2Color":"#000000",
        "eye3Color":"#000000",
        "eyeBall1Color":"#000000",
        "eyeBall2Color":"#000000",
        "eyeBall3Color":"#000000",
        "gradientColor1":"",
        "gradientColor2":"",
        "gradientType":"linear",
        "gradientOnEyes":"true",
        "logo":"",
        "logoMode":"default"
    },
    "size":1000,
    "download":"imageUrl",
    "file":"png"
}




@user.on_message(user.sudo & user.command("qrGen"))
async def _(_, message: user.types.Message):
    if len(message.text.split()) == 1:
        return await message.delete()
    data = _gen(message.text.split(None, 1)[1])
    await message.reply_document(
        (await user.postRequest(
            'https://api.qrcode-monkey.com//qr/custom',
            json=data
            )
        )['imageUrl'].replace(
            '//api', 'https://api'
            ),
        quote=True
    )

@user.on_message(user.sudo & user.command("qrRead"))
async def _(_, message: user.types.Message):
    if not message.reply_to_message:
        return await message.delete()
    if message.reply_to_message.document or message.reply_to_message.photo:
        f = await message.reply_to_message.download()
        for x in BarCodeReader().decode(f):
            out = reFresh(x)
        doc = user.md.KanTeXDocument()
        sec = user.md.Section('qrCode Decoded:')
        for key, value in out.items():
            sec.append(user.md.KeyValueItem(user.md.Bold(key), user.md.Code(value)))
        doc.append(sec)
        try:
            await message.reply(doc, quote=True)
        except errors.exceptions.bad_request_400.MessageTooLong:
            data = BytesIO(str(out).encode())
            data.name = 'qrRead.txt'
            await message.reply_document(
                document=data,
                quote=True
            )
        os.remove(f)



def reFresh(content: dict):
    temp = {}
    for key, value in content.items():
        try:
            temp[key] = value.decode('utf-8')
        except AttributeError:
            ...
    return temp