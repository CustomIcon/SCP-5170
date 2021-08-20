from scp import user


__PLUGIN__ = 'follow'
__DOC__ = str(user.md.KanTeXDocument(
    user.md.Section('HTTP(s) Tools',
        user.md.SubSection('Redirect',
            user.md.Code('(*prefix)url {url}')),
        user.md.SubSection('IpInfo',
            user.md.Code('(*prefix)dns {ip_address} - * optional')))))


@user.on_message(user.sudo & user.command('url'))
async def _(_, message: user.types.Message):
    if len(message.command) == 1:
        return await message.delete()
    link = message.command[1]
    text = user.md.KanTeXDocument(
        user.md.Section('Redirect',
                user.md.KeyValueItem(
                    user.md.Bold('Original URL'),user.md.Code(link)),
                user.md.KeyValueItem(
                    user.md.Bold('Followed URL'),
                    user.md.Code(await user.resolve_url(link, base_domain=False)))))
    await message.reply(text, quote=True)


@user.on_message(user.filters.me & user.command('dns'))
async def _(_, message: user.types.Message):
    if len(message.command) == 1:
        query = ''
    else:
        query = message.command[1]
    doc = user.md.KanTeXDocument()
    sec = user.md.Section(f'IP-info: `{query}`')
    for key, value in (await user.getRequest('http://ip-api.com/json/' + query)).items():
        sec.append(user.md.KeyValueItem(user.md.Bold(key), user.md.Code(value)))
    doc.append(sec)
    await message.reply(doc, quote=True)


