from scp.utils.selfInfo import updateInfo
import importlib
from scp import bot, user
from scp.plugins.bot import ALL_SETTINGS
from scp.plugins.user import ALL_MODULES
import asyncio


async def reinitial_restart():
    await updateInfo()


async def reinitial():
    await asyncio.gather(
        user.start(),
        bot.start(),
        updateInfo(),
        user.stop(),
        bot.stop(),
    )


async def reload_userbot():
    await user.start()
    for modul in ALL_MODULES:
        imported_module = importlib.import_module('scp.plugins.user.' + modul)
        importlib.reload(imported_module)


async def restart_all():
    # Restarting and load all plugins
    asyncio.get_event_loop().create_task(reboot())


async def reboot():
    global BOT_RUNTIME, HELP_COMMANDS
    importlib.reload(importlib.import_module('scp.plugins.user'))
    importlib.reload(importlib.import_module('scp.plugins.bot'))
    await asyncio.gather(bot.restart(), user.restart(), reinitial_restart())
    BOT_RUNTIME = 0
    HELP_COMMANDS = {}
    # Assistant bot
    for setting in ALL_SETTINGS:
        imported_module = importlib.import_module(
            'scp.plugins.bot.' + setting,
        )
        importlib.reload(imported_module)
    for modul in ALL_MODULES:
        imported_module = importlib.import_module('scp.plugins.user.' + modul)
        if hasattr(
            imported_module,
            '__PLUGIN__',
        ) and imported_module.__PLUGIN__:
            imported_module.__PLUGIN__ = imported_module.__PLUGIN__
        if hasattr(
            imported_module,
            '__PLUGIN__',
        ) and imported_module.__PLUGIN__:
            if imported_module.__PLUGIN__.lower() not in HELP_COMMANDS:
                HELP_COMMANDS[
                    imported_module.__PLUGIN__.lower()
                ] = imported_module
            else:
                raise Exception(
                    "Can't have two modules with the same name!",
                )
        if hasattr(imported_module, '__DOC__') and imported_module.__DOC__:
            HELP_COMMANDS[imported_module.__PLUGIN__.lower()] = imported_module
        importlib.reload(imported_module)
