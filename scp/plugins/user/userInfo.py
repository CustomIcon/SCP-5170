from scp import user, bot
from scp.utils.selfInfo import info
from pyrogram import errors


__PLUGIN__ = 'UserInfo'
__DOC__ = str(user.md.KanTeXDocument(
    user.md.Section('Chat information resolver',
        user.md.SubSection('user info',
            user.md.Code('(*prefix)info {chat_id} or {user_id}')))))


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
        x = await user.get_inline_bot_results(info['_bot_username'], '_userInfo ' + str(Uid))
    except (
        errors.exceptions.bad_request_400.PeerIdInvalid,
        errors.exceptions.bad_request_400.BotResponseTimeout
    ) as err:
        return await message.reply(err, quote=True)
    for m in x.results:
        await message.reply_inline_bot_result(x.query_id, m.id, quote=True)


@bot.on_inline_query(user.filters.user(info['_user_id']) & user.filters.regex('^_userInfo'))
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
    if isinstance(u, user.types.Chat):
        text = user.md.Section(
            'ChatInfo:',
            user.md.KeyValueItem(key='chat_id', value=u.id),
            user.md.KeyValueItem(key='type', value=u.type),
            user.md.KeyValueItem(key='title', value=u.title),
            user.md.KeyValueItem(key='invite_link', value=u.invite_link),
            user.md.KeyValueItem(key='members_count', value=u.members_count),
            user.md.KeyValueItem(key='dc_id', value=u.dc_id),
            user.md.KeyValueItem(key='username', value=u.username)
        )
        keyboard = user.types.InlineKeyboardMarkup(
            [
                [
                    user.types.InlineKeyboardButton('Permissions', callback_data=f'cperm_{u.id}'),
                    user.types.InlineKeyboardButton('Description', callback_data=f'cdesc_{u.id}')
                ]
            ]
         ) if u.permissions else None
    else:
        text = user.md.Section(
            'UserInfo:',
            user.md.KeyValueItem(key='user_id', value=u.id),
            user.md.KeyValueItem(key='is_contact', value=u.is_contact),
            user.md.KeyValueItem(key='first_name', value=u.first_name),
            user.md.KeyValueItem(key='last_name', value=u.last_name),
            user.md.KeyValueItem(key='username', value=u.username),
            user.md.KeyValueItem(key='dc_id', value=u.dc_id)
        )
        keyboard = user.types.InlineKeyboardMarkup(
            [[user.types.InlineKeyboardButton('UserLink', url=f'tg://user?id={u.id}'), user.types.InlineKeyboardButton('Description', callback_data=f'cdesc_{u.id}')]]
        )
    answers.append(
        user.types.InlineQueryResultArticle(
            title='Info',
            input_message_content=user.types.InputTextMessageContent(text),
            reply_markup=keyboard
        )
    )
    await query.answer(
        answers,
        cache_time=0,

    )


def bool_check(var: bool):
    if var:
        return "✅"
    else:
        return "❌"


def _text(perms):
    text = ''
    text += 'Message: ' + bool_check(perms.can_send_messages) + '\n'
    text += 'Media: ' + bool_check(perms.can_send_media_messages) + '\n'
    text += 'Sticker: ' + bool_check(perms.can_send_stickers) + '\n'
    text += 'GIF: ' + bool_check(perms.can_send_animations) + '\n'
    text += 'Game: ' + bool_check(perms.can_send_games) + '\n'
    text += 'Inline: ' + bool_check(perms.can_use_inline_bots) + '\n'
    text += 'Web: ' + bool_check(perms.can_add_web_page_previews) + '\n'
    text += 'Poll: ' + bool_check(perms.can_send_polls) + '\n'
    text += 'Info: ' + bool_check(perms.can_change_info) + '\n'
    text += 'invite: ' + bool_check(perms.can_invite_users) + '\n'
    text += 'Pin: ' + bool_check(perms.can_pin_messages) + '\n'
    return text


@bot.on_callback_query(bot.sudo & bot.filters.regex('^cperm_'))
async def _(_, query:user.types.CallbackQuery):
    await query.answer(
        _text(
            (await user.get_chat(int(query.data.split("_")[1]))).permissions
        ), show_alert=True)


@bot.on_callback_query(bot.sudo & bot.filters.regex('^cdesc_'))
async def _(_, query:user.types.CallbackQuery):
    chat = await user.get_chat(int(query.data.split("_")[1]))
    await query.answer(
        chat.description[:150] if chat.description else chat.bio, show_alert=True)