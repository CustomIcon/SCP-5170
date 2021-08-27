from scp import user


__PLUGIN__ = 'phoneValidate'
__DOC__ = str(
    user.md.KanTeXDocument(
        user.md.Section(
            'phoneValidate',
            user.md.SubSection(
                'validate a phone number',
                user.md.Code('(*prefix)phoneValidate {phone_number}'),
            ),
        ),
    ),
)


@user.on_message(user.sudo & user.command('phoneValidate'))
async def _(_, message: user.types.Message):
    if len(message.text.split()) == 1:
        return await message.delete()
    resp = await user.getRequest(
        'https://phonevalidation.abstractapi.com/v1/'
        '?api_key=9d5acbb007c74165b9702ec4a7246e81&'
        f'phone={message.text.split(None, 1)[1]}',
    )
    doc = user.md.KanTeXDocument()
    sec = user.md.Section('PhoneValidation:')
    for x, y in resp.items():
        if isinstance(y, dict):
            subsec = user.md.SubSection(x)
            for i, n in y.items():
                subsec.append(
                    user.md.KeyValueItem(user.md.Bold(i), user.md.Code(n)),
                )
            sec.append(subsec)
        else:
            sec.append(
                user.md.KeyValueItem(
                    user.md.Bold(x), user.md.Code(y),
                ),
            )
    doc.append(sec)
    await message.reply(doc, quote=True)
