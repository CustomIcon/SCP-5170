from scp import user


__PLUGIN__ = 'createGroup'
__DOC__ = str(user.md.KanTeXDocument(
    user.md.Section('createGroup',
        user.md.SubSection('create a super group / channel',
            user.md.Code('(*prefix)create {type} {title}')))))



@user.on_message(user.sudo & user.command('create'))
async def _(_, message: user.types.Message):
    if len(message.command) == 1:
        return await message.delete()
    arg = message.text.split(None, 1)[1].split(None, 1)
    if len(arg) == 1:
        return await message.reply(
            user.md.KanTeXDocument(user.md.Section('Error',
            user.md.Italic('title is not given'))),
            quote=True
        )
    if arg[0].lower() not in ['group', 'channel']:
        return await message.reply(
            user.md.KanTeXDocument(user.md.Section('Error',
            user.md.Italic(f'{arg[0].lower()} is not in [\'group\', \'channel\']'))),
            quote=True
        )
    if arg[0].lower() == 'group':
        chat = await user.create_supergroup(title=arg[1])
    elif arg[0].lower() == 'channel':
        chat = await user.create_channel(title=arg[1])
    link = await user.export_chat_invite_link(chat.id)
    await message.reply(
        user.md.KanTeXDocument(
            user.md.Section('Create Chat',
                user.md.SubSection(chat.title,
                    user.md.KeyValueItem(user.md.Bold('id'), user.md.Code(chat.id)),
                    user.md.KeyValueItem(user.md.Bold('type'), user.md.Code(chat.type)),
                    user.md.KeyValueItem(user.md.Bold('link'), link),))
        )
    )