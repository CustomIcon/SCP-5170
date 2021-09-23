from scp import user
import os


__PLUGIN__ = 'DirectLink'
__DOC__ = str(
    user.md.KanTeXDocument(
        user.md.Section(
            'upload files to anonfiles.com',
            user.md.SubSection(
                'upload a file',
                user.md.Code('(*prefix)uploadFile {replyMedia}'),
            ),
        ),
    ),
)


@user.on_message(
    user.sudo
    & (user.filters.reply | ~user.filters.text)
    & user.command('uploadFile'),
)
async def _(_, message: user.types.Message):
    f = await message.reply_to_message.download()
    r = await message.reply('**Uploading**', quote=True)
    out = await user.Request(
        'https://api.anonfiles.com/upload',
        type='post',
        data={'file': open(f, 'rb')},
    )
    os.remove(f)
    if out['status']:
        text = user.md.KanTeXDocument(
            user.md.Section(
                'FileUploaded',
                user.md.KeyValueItem(
                    user.md.Bold('id'),
                    user.md.Code(
                        out['data']['file']['metadata']['id'],
                    ),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'size',
                    ),
                    user.md.Code(
                        out['data']['file']['metadata']['size']['readable'],
                    ),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'link',
                    ),
                    user.md.Link(
                        out['data']['file']['metadata']['name'],
                        out['data']['file']['url']['short'],
                    ),
                ),
            ),
        )
        return await r.edit(text)
