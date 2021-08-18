import re
from typing import List
from pyrogram.filters import create
from pyrogram.types import Message
from pyrogram import Client
from configparser import ConfigParser
from scp.utils.selfInfo import info

config = ConfigParser()
config.read('config.ini')
prefixes = config.get('scp-5170', 'prefixes').split()


def user_command(
    commands: str or List[str],
    prefixes: str or List[str] = prefixes,
    case_sensitive: bool = False,
):
    """
    This is a drop in replacement for the default filters.command that is included
    in Pyrogram. The Pyrogram one does not support /command@botname type commands,
    so this custom filter enables that throughout all groups and private chats.
    This filter works exactly the same as the original command filter even with support for multiple command
    prefixes and case sensitivity.
    Command arguments are given to user as message.command
    """

    async def func(flt, _: Client, message: Message):
        text: str = message.text or message.caption
        message.command = None
        if not text:
            return False
        regex = r'(?i)^({prefix})({regex})(@{bot_name})?(\s.*)?$'.format(
            prefix='|'.join(re.escape(x) for x in flt.prefixes),
            regex='|'.join(flt.commands),
            bot_name=info['_user_username'].lower(),
        )
        if matches := re.search(regex, text, flags=re.IGNORECASE):
            message.command = [matches.group(2)]
            if matches.group(4):  # The command has arguments
                message.command.extend(
                    [arg for arg in matches.group(4).strip().split()],
                )
            return True
        return False
    commands = commands if isinstance(commands, list) else [commands]
    commands = {c if case_sensitive else c.lower() for c in commands}
    prefixes = prefixes or []
    prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    prefixes = set(prefixes) if prefixes else {''}
    return create(
        func,
        'CustomUserCommandFilter',
        commands=commands,
        prefixes=prefixes,
        case_sensitive=case_sensitive,
    )


def bot_command(
    commands: str or List[str],
    prefixes: str or List[str] = prefixes,
    case_sensitive: bool = False,
):
    """
    This is a drop in replacement for the default filters.command that is included
    in Pyrogram. The Pyrogram one does not support /command@botname type commands,
    so this custom filter enables that throughout all groups and private chats.
    This filter works exactly the same as the original command filter even with support for multiple command
    prefixes and case sensitivity.
    Command arguments are given to user as message.command
    """

    async def func(flt, _: Client, message: Message):
        text: str = message.text or message.caption
        message.command = None
        if not text:
            return False
        regex = r'(?i)^({prefix})({regex})(@{bot_name})?(\s.*)?$'.format(
            prefix='|'.join(re.escape(x) for x in flt.prefixes),
            regex='|'.join(flt.commands),
            bot_name=info['_bot_username'].lower(),
        )
        if matches := re.search(regex, text, flags=re.IGNORECASE):
            message.command = [matches.group(2)]
            if matches.group(4):  # The command has arguments
                message.command.extend(
                    [arg for arg in matches.group(4).strip().split()],
                )
            return True
        return False
    commands = commands if isinstance(commands, list) else [commands]
    commands = {c if case_sensitive else c.lower() for c in commands}
    prefixes = prefixes or []
    prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    prefixes = set(prefixes) if prefixes else {''}
    return create(
        func,
        'CustomBotCommandFilter',
        commands=commands,
        prefixes=prefixes,
        case_sensitive=case_sensitive,
    )