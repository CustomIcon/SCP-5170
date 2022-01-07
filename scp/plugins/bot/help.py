import re
from scp import bot, user
from scp.core.filters.Command import prefixes
from scp.core.functions.plugins import HELP_COMMANDS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from scp.utils.misc import paginate_modules
from scp.utils.selfInfo import info  # type: ignore


async def help_parser(client, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(
            paginate_modules(0, HELP_COMMANDS, 'help'),
        )
    await client.send_message(chat_id, text, reply_markup=keyboard)


@bot.on_inline_query(
    user.filters.user(
        info['_user_id'],
    )
    & user.filters.regex('^help'),
)
async def _(_, query: bot.types.InlineQuery):
    keyboard = bot.types.InlineKeyboardMarkup(
        paginate_modules(0, HELP_COMMANDS, 'help'),
    )
    ans = [
        user.types.InlineQueryResultArticle(
            title='help',
            input_message_content=user.types.InputTextMessageContent(
                user.md.KanTeXDocument(
                    user.md.Section(
                        'Help module',
                        user.md.KeyValueItem(
                            user.md.Bold(
                                'Prefixes',
                            ), user.md.Code(', '.join(prefixes)),
                        ),
                    ),
                ),
            ),
            reply_markup=keyboard,
        ),
    ]
    await query.answer(ans, cache_time=0)


@bot.on_message(
    (bot.filters.user(bot._sudo) | bot.filters.user(info['_user_id']))
    & bot.command('help', prefixes='/'),
)
async def help_command(client, message):
    await help_parser(
        client,
        message.chat.id,
        user.md.KanTeXDocument(
            user.md.Section(
                'Help module',
                user.md.KeyValueItem(
                    user.md.Bold(
                        'Prefixes',
                    ), user.md.Code(', '.join(prefixes)),
                ),
            ),
        ),
    )


async def help_button_callback(_, __, query):
    if re.match(r'help_', query.data):
        return True


help_button_create = bot.filters.create(help_button_callback)


async def editMessage(
    query,
    text=str,
    reply_markup: bot.types.InlineKeyboardMarkup = None,
    disable_web_page_preview: bool = None
):
    try:
        return await query.message.edit(
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
        )
    except AttributeError:
        return await bot.edit_inline_text(
            query.inline_message_id,
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
        )


@bot.on_callback_query(
    help_button_create
    & (bot.filters.user(bot._sudo) | bot.filters.user(info['_user_id'])),
)
async def help_button(_, query):
    mod_match = re.match(r'help_module\((.+?)\)', query.data)
    prev_match = re.match(r'help_prev\((.+?)\)', query.data)
    next_match = re.match(r'help_next\((.+?)\)', query.data)
    back_match = re.match(r'help_back', query.data)
    create_match = re.match(r'help_create', query.data)
    if mod_match:
        module = mod_match.group(1)
        text = (
            'Document for **{}**:\n'.format(
                HELP_COMMANDS[module].__PLUGIN__,
            )
            + HELP_COMMANDS[module].__DOC__.replace(
                '(*prefix)',
                user._config.get(
                    'scp-5170',
                    'prefixes',
                ).split()[0],
            )
        )

        await editMessage(
            query,
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text='Back',
                            callback_data='help_back',
                        ),
                    ],
                ],
            ),
            disable_web_page_preview=True,
        )

    elif prev_match:
        curr_page = int(prev_match.group(1))
        await editMessage(
            query,
            text=user.md.KanTeXDocument(
                user.md.Section(
                    'Help module',
                    user.md.KeyValueItem(
                        user.md.Bold('Prefixes'),
                        user.md.Code(' '.join(prefixes)),
                    ),
                ),
            ),
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(curr_page - 1, HELP_COMMANDS, 'help'),
            ),
            disable_web_page_preview=True,
        )

    elif next_match:
        next_page = int(next_match.group(1))
        await editMessage(
            query,
            text=user.md.KanTeXDocument(
                user.md.Section(
                    'Help module',
                    user.md.KeyValueItem(
                        user.md.Bold('Prefixes'),
                        user.md.Code(' '.join(prefixes)),
                    ),
                ),
            ),
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(next_page + 1, HELP_COMMANDS, 'help'),
            ),
            disable_web_page_preview=True,
        )

    elif back_match:
        await editMessage(
            query,
            text=user.md.KanTeXDocument(
                user.md.Section(
                    'Help module',
                    user.md.KeyValueItem(
                        user.md.Bold('Prefixes'),
                        user.md.Code(' '.join(prefixes)),
                    ),
                ),
            ),
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, HELP_COMMANDS, 'help'),
            ),
            disable_web_page_preview=True,
        )

    elif create_match:
        text, keyboard = await help_parser(query)
        await editMessage(
            query,
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

    return await query.answer()
