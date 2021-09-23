import re
from scp import bot, user
from scp.core.filters.Command import prefixes
from scp.core.functions.plugins import HELP_COMMANDS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from scp.utils.misc import paginate_modules
from scp.utils.selfInfo import info


async def help_parser(client, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(
            paginate_modules(0, HELP_COMMANDS, 'help'),
        )
    await client.send_message(chat_id, text, reply_markup=keyboard)


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


@bot.on_callback_query(help_button_create)
async def help_button(_, query):
    mod_match = re.match(r'help_module\((.+?)\)', query.data)
    back_match = re.match(r'help_back', query.data)
    if mod_match:
        module = mod_match.group(1)
        text = (
            'Document for **{}**:\n'.format(
                HELP_COMMANDS[module].__PLUGIN__,
            )
            + HELP_COMMANDS[module].__DOC__
        )

        await query.message.edit(
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
        )

    elif back_match:
        await query.message.edit(
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
        )
    await query.answer()
