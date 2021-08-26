from scp import user, bot
from scp.utils.selfInfo import info
from scp.utils.strUtils import name_check, permissionParser
from pyrogram import errors


__PLUGIN__ = 'UserInfo'
__DOC__ = str(
    user.md.KanTeXDocument(
        user.md.Section(
            'Chat information resolver',
            user.md.SubSection(
                'user info',
                user.md.Code('(*prefix)info {chat_id} or {user_id}'),
            ),
        ),
    ),
)


@user.on_message(
    user.sudo &
    user.command('info'),
)
async def _(_, message: user.types.Message):
    cmd = message.command
    if not message.reply_to_message and len(cmd) == 1:
        get_user = message.from_user.id
    elif len(cmd) == 1:
        if message.reply_to_message.forward_from:
            get_user = message.reply_to_message.forward_from.id
        else:
            get_user = message.reply_to_message.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]
        try:
            get_user = int(cmd[1])
        except ValueError:
            pass
    try:
        Uid = (await user.get_chat(get_user)).id
        x = await user.get_inline_bot_results(
            info['_bot_username'],
            '_userInfo ' + str(Uid),
        )
    except (
        errors.exceptions.bad_request_400.PeerIdInvalid,
        errors.exceptions.bad_request_400.BotResponseTimeout,
    ) as err:
        return await message.reply(err, quote=True)
    for m in x.results:
        await message.reply_inline_bot_result(x.query_id, m.id, quote=True)


@bot.on_inline_query(
    user.filters.user(
        info['_user_id'],
    )
    & user.filters.regex('^_userInfo'),
)
async def _(_, query: bot.types.InlineQuery):
    try:
        answers = []
        get_user = int(query.query.split(' ')[1])
    except (ValueError, IndexError):
        return None
    try:
        u = await user.get_users(get_user)
    except errors.exceptions.bad_request_400.PeerIdInvalid:
        return None
    except IndexError:
        u = await user.get_chat(get_user)
    try:
        onlines = (
            await user.send(
                user.raw.functions.messages.GetOnlines(
                    peer=await user.resolve_peer(get_user),
                ),
            )
        ).onlines
    except errors.exceptions.bad_request_400.PeerIdInvalid:
        onlines = 0
    if isinstance(u, user.types.Chat):
        text = user.md.Section(
            'ChatInfo:',
            user.md.SubSection(
                user.md.KeyValueItem('title', u.title),
                user.md.KeyValueItem(
                    user.md.Bold('chat_id'), user.md.Code(u.id),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('type'), user.md.Code(u.type),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('title'), user.md.Code(u.title),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('invite_link'), user.md.Code(u.invite_link),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('members_count'), user.md.Code(
                        u.members_count,
                    ),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('dc_id'), user.md.Code(u.dc_id),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('online_count'), user.md.Code(str(onlines)),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('username'), user.md.Code(
                        name_check(u.username),
                    ),
                ),
            ),
        )
        keyboard = user.types.InlineKeyboardMarkup(
            [
                [
                    user.types.InlineKeyboardButton(
                        'Permissions', callback_data=f'cperm_{u.id}',
                    ),
                    user.types.InlineKeyboardButton(
                        'Description', callback_data=f'cdesc_{u.id}',
                    ),
                ],
            ],
        ) if u.permissions else None
    else:
        text = user.md.Section(
            'UserInfo:',
            user.md.SubSection(
                user.md.KeyValueItem(
                    key='name', value=u.first_name + ' ' + (u.last_name or ''),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'user_id',
                    ), user.md.Code(u.id),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'is_contact',
                    ), user.md.Code(u.is_contact),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'username',
                    ), user.md.Code(name_check(u.username)),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'dc_id',
                    ), user.md.Code(u.dc_id),
                ),
            ),
        )
        keyboard = user.types.InlineKeyboardMarkup(
            [[
                user.types.InlineKeyboardButton(
                    'UserLink',
                    url=f'tg://user?id={u.id}',
                ),
                user.types.InlineKeyboardButton(
                    'Description', callback_data=f'cdesc_{u.id}',
                ),
            ]],
        )
    answers.append(
        user.types.InlineQueryResultArticle(
            title='Info',
            input_message_content=user.types.InputTextMessageContent(text),
            reply_markup=keyboard,
        ),
    )
    await query.answer(
        answers,
        cache_time=0,

    )


@bot.on_callback_query(
    (bot.sudo | bot.filters.user(info['_user_id']))
    & bot.filters.regex('^cperm_'),
)
async def _(_, query: user.types.CallbackQuery):
    await query.answer(
        permissionParser(
            (await user.get_chat(int(query.data.split('_')[1]))).permissions,
        ), show_alert=True,
    )


@bot.on_callback_query(
    (bot.sudo | bot.filters.user(info['_user_id']))
    & bot.filters.regex('^cdesc_'),
)
async def _(_, query: user.types.CallbackQuery):
    chat = await user.get_chat(int(query.data.split('_')[1]))
    await query.answer(
        chat.description[:150] if chat.description else chat.bio,
        show_alert=True,
    )
