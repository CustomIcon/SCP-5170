from scp import user
from base64 import b64encode as Base64
import ujson as json


__PLUGIN__ = 'Grabify'
__DOC__ = str(
    user.md.KanTeXDocument(
        user.md.Section(
            'Create short-links to grab IP Addresses',
            user.md.SubSection(
                'grabify',
                user.md.Code('(*prefix)grabiFy {link}'),
            ),
        ),
    ),
)


@user.on_message(user.sudo & user.command('grabiFy'))
async def _(_, message: user.types.Message):
    if len(message.text.split()) == 1:
        return await message.delete()
    b64Decode = Base64(message.text.split(None, 1)[1].encode('utf-8'))
    _r = await user.Request(
        f'https://linkify.me/api/?destination={b64Decode.decode("utf-8")}',
        type='get',
    )
    data = json.loads(_r)
    text = user.md.KanTeXDocument(
        user.md.Section(
            'Ip Grabber',
            user.md.KeyValueItem(
                user.md.Bold('Link'),
                user.md.Code(
                    'https://linkify.me/' + data['linkify'],
                ),
            ),
            user.md.KeyValueItem(
                user.md.Bold('track_point'),
                user.md.Link(
                    data['tracking_code'],
                    'https://linkify.me/tc/' +
                    data['tracking_code'],
                ),
            ),
        ),
    )
    await message.reply(
        text,
        disable_web_page_preview=True,
        quote=True,
    )
