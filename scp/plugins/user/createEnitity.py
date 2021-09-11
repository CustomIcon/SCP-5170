import asyncio
import base64
import binascii
import re
from scp import user


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
        await user.send_message('BotFather', '/newbot')
        await asyncio.sleep(0.5)
        await user.send_message('Botfather', arg[1])
        await asyncio.sleep(0.5)
        botName = arg[1].replace(' ', '_') + '_bot'
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
        validate, token = check(ans.text)
        if validate:
            return await message.reply(
                user.md.KanTeXDocument(
                    user.md.Section(
                        'Generated Token',
                        user.md.KeyValueItem(
                            user.md.Code(
                                botName,
                            ),
                            user.md.Code(token),
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


def validate(token: str) -> bool:
    t = token.partition(':')
    try:
        decode = base64.urlsafe_b64decode(f'{t[-1]}====')
    except binascii.Error:
        return False
    return all(
        (
            t[0].isdecimal(),
            decode[:2].startswith(b'\x00\x01'),
            len(decode),
        ),
    )


def check(token: str) -> bool:
    token = re.findall(r'[0-9]{10}:[a-zA-Z0-9_-]{35}', token)
    if len(token) == 0:
        return False, False
    else:
        return True, token[0]
