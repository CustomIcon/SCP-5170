from scp import user, bot
from scp.utils.selfInfo import info
from pyrogram import errors


chats = user.filters.chat()
_chats = {}


@user.on_message(chats, group=100)
async def _(_, message: user.types.Message):
    for x, y in _chats.items():
        if x == message.chat.id:
            await user.forward_messages(y, x, message.message_id)


@user.on_message(user.sudo & user.command('pipe'))
async def _(_, message: user.types.Message):
    fromChat = int(message.text.split(' ')[1])
    toChat = int(message.text.split(' ')[2])
    chats.add(fromChat)
    chats.add(toChat)
    _chats[fromChat] = toChat
    print(chats)


@user.on_message(user.sudo & user.command('listPipes'))
async def _(_, message: user.types.Message):
    try:
        x = await user.get_inline_bot_results(
            info['_bot_username'],
            'pipeList',
        )
    except (
        errors.exceptions.bad_request_400.PeerIdInvalid,
        errors.exceptions.bad_request_400.BotResponseTimeout,
    ):
        return await message.reply('no pipes', quote=True)
    if len(_chats) == 0:
        return await message.reply('No pipes running')
    for m in x.results:
        await message.reply_inline_bot_result(x.query_id, m.id, quote=True)


@bot.on_inline_query(
    user.filters.user(info['_user_id'])
    & user.filters.regex('^pipeList'),
)
async def _(_, query: user.types.InlineQuery):
    buttons = []
    for x, _ in _chats.items():
        buttons.append(
            [user.types.InlineKeyboardButton(x, callback_data=f'pipeCheck_{x}')]
        )
    await query.answer(
        results=[
            user.types.InlineQueryResultArticle(
                title='list pipes',
                input_message_content=user.types.InputTextMessageContent(
                    user.md.KanTeXDocument(
                        user.md.Section(
                            'ListPipes',
                            user.md.KeyValueItem(
                                'Pipes Running',
                                str(len(_chats)),
                            ),
                        ),
                    ),
                ),
                reply_markup=user.types.InlineKeyboardMarkup(buttons),
            ),
        ],
        cache_time=0
    ) 


@bot.on_callback_query(
    user.filters.user(info['_user_id'])
    & user.filters.regex('^pipeCheck_'),
)
async def _(_, query: user.types.CallbackQuery):
    fromChat = int(query.data.split('_')[1])
    for x, y in _chats.items():  
        if x == fromChat:
            _fromChat = (await user.get_chat(x))
            _toChat = (await user.get_chat(y))
            fromChat = (_fromChat.first_name or _fromChat.last_name or _fromChat.title, _fromChat.id)
            toChat = (_toChat.first_name or _toChat.id)
            return await query.edit_message_text(
                user.md.KanTeXDocument(
                    user.md.Section('PipeChat',
                    user.md.KeyValueItem('fromChat', str(fromChat)),
                    user.md.KeyValueItem('toChat', str(toChat)))
                ),
                reply_markup=user.types.InlineKeyboardMarkup(
                    [[user.types.InlineKeyboardButton('removePipe', f'pipeRemove_{x}_{y}')]]
                )
            )

@bot.on_callback_query(
    user.filters.user(info['_user_id'])
    & user.filters.regex('^pipeRemove_'),
)
async def _(_, query: user.types.CallbackQuery):
    fromChat = int(query.data.split('_')[1])
    toChat = int(query.data.split('_')[2])
    chats.remove(fromChat)
    chats.remove(toChat)
    _chats.pop(fromChat)
    await query.edit_message_text(user.md.KanTeXDocument(
        user.md.Section('Pipe Removed',
        user.md.KeyValueItem(fromChat, toChat))
    ))
