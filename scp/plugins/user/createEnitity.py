import asyncio
from scp import user
from scp.utils import parser


__PLUGIN__ = 'create'
__DOC__ = str(
    user.md.KanTeXDocument(
        user.md.Section(
            'create',
            user.md.SubSection(
                'create a super group / channel / bot',
                user.md.Code('(*prefix)create {type} {title}'),
            ),
        ),
    ),
)


convLock = asyncio.Lock()


@user.on_message(user.sudo & user.command('create'))
async def _(_, message: user.types.Message):
    if len(message.command) == 1:
        return await message.delete()
    arg = message.text.split(None, 1)[1].split(None, 1)
    if len(arg) == 1:
        return await message.reply(
            user.md.KanTeXDocument(
                user.md.Section(
                    'Error',
                    user.md.Italic('title is not given'),
                ),
            ),
            quote=True,
        )
    if arg[0].lower() not in ['group', 'channel', 'bot']:
        return await message.reply(
            user.md.KanTeXDocument(
                user.md.Section(
                    'Error',
                    user.md.Italic(
                        f'{arg[0].lower()}'
                        'is not in [\'group\', \'channel\', \'bot\']',
                    ),
                ),
            ),
            quote=True,
        )
    if arg[0].lower() == 'group':
        chat = await user.create_supergroup(title=arg[1])
    elif arg[0].lower() == 'channel':
        chat = await user.create_channel(title=arg[1])
    elif arg[0].lower() == 'bot':
        async with convLock:
            await user.send_message('BotFather', '/newbot')
            await asyncio.sleep(0.5)
            await user.send_message('Botfather', arg[1])
            await asyncio.sleep(0.5)
        botName = arg[1].replace(' ', '_')
        ans = await user.ask('Botfather', botName)
        if not ans.text.startswith('Done!'):
            return await message.reply(
                user.md.KanTeXDocument(
                    user.md.Section(
                        'Error',
                        user.md.Italic(
                            f'@{botName} is taken',
                        ),
                    ),
                ),
                quote=True,
            )
        validate, token = parser.checkToken(ans.text)
        if validate:
            return await message.reply(
                user.md.KanTeXDocument(
                    user.md.Section(
                        'Generated Token',
                        user.md.KeyValueItem(
                            user.md.Code(
                                '@' + botName,
                            ),
                            user.md.Code(token),
                        ),
                        user.md.KeyValueItem(
                            user.md.Bold('Link'),
                            f't.me/{botName}',
                        ),
                    ),
                ),
                quote=True,
            )

    link = await user.export_chat_invite_link(chat.id)
    await message.reply(
        user.md.KanTeXDocument(
            user.md.Section(
                'Create Chat',
                user.md.SubSection(
                    chat.title,
                    user.md.KeyValueItem(
                        user.md.Bold(
                            'id',
                        ), user.md.Code(chat.id),
                    ),
                    user.md.KeyValueItem(
                        user.md.Bold(
                            'type',
                        ), user.md.Code(chat.type),
                    ),
                    user.md.KeyValueItem(user.md.Bold('link'), link),
                ),
            ),
        ),
    )
