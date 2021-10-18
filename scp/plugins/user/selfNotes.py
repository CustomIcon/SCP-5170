from scp import user
from scp.database.tables.notes import Notes


@user.on_message(user.filters.me & user.command('notes'))
async def _(_, message: user.types.Message):
    data = await Notes().load()
    doc = user.md.KanTeXDocument()
    sec = user.md.Section(f'Notes {len(data)}')
    for key, _ in data.items():
        sec.append(user.md.Code(key))
    doc.append(sec)
    return await message.reply(doc, quote=True)


@user.on_message(user.filters.me & user.command('addNote'))
async def _(_, message: user.types.Message):
    data = await Notes().load()
    args = message.text.split(None, 2)
    data[args[1]] = args[2]
    await Notes().dump(data)
    return await message.reply(
        user.md.KanTeXDocument(
            user.md.Section(
                'Note Saved.',
                user.md.Code(f'Note Added "{args[1]}"'),
            ),
        ),
        quote=True,
    )


@user.on_message(user.filters.me & user.command('getNote'))
async def _(_, message: user.types.Message):
    data = await Notes().load()
    doc = user.md.KanTeXDocument()
    for key, value in data.items():
        if message.command[1] == key:
            sec = user.md.Section(key)
            sec.append(user.md.Code(value))
            doc.append(sec)
            return await message.reply(doc, quote=True)
        else:
            sec = user.md.Section(
                'Error',
                user.md.Code('Cannot find the note'),
            )
    doc.append(sec)
    return await message.reply(doc, quote=True)


@user.on_message(user.filters.me & user.command('deleteNote'))
async def _(_, message: user.types.Message):
    data = await Notes().load()
    if data.get(message.command[1], None):
        data.pop(message.command[1])
        await Notes().dump(data)
        return await message.reply(
            user.md.KanTeXDocument(
                user.md.Section(
                    'Note Deleted,',
                    user.md.Code(f'Note "{message.command[1]}" deleted.'),
                ),
            ),
            quote=True,
        )
    return await message.reply(
        user.md.KanTeXDocument(
            user.md.Section(
                'Error',
                user.md.Code('Cannot find the note'),
            ),
        ),
        quote=True,
    )
