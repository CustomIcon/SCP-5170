import importlib
from scp.plugins.bot import ALL_SETTINGS
from scp.plugins.user import ALL_MODULES

HELP_COMMANDS = {}

async def loadBotPlugins():
    for setting in ALL_SETTINGS:
        importlib.import_module(
            'scp.plugins.bot.' + setting,
        )

async def loadUserPlugins():
    for modul in ALL_MODULES:
        imported_module = importlib.import_module('scp.plugins.user.' + modul)
        if hasattr(
            imported_module,
            '__MODULE__',
        ) and imported_module.__MODULE__:
            imported_module.__MODULE__ = imported_module.__MODULE__
        if hasattr(
            imported_module,
            '__MODULE__',
        ) and imported_module.__MODULE__:
            if imported_module.__MODULE__.lower() not in HELP_COMMANDS:
                HELP_COMMANDS[
                    imported_module.__MODULE__.lower()
                ] = imported_module
            else:
                raise Exception(
                    "Can't have two modules with the same name!",
                )
        if hasattr(imported_module, '__HELP__') and imported_module.__HELP__:
            HELP_COMMANDS[imported_module.__MODULE__.lower()] = imported_module