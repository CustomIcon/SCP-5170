from pyrogram import Client, filters, types
from scp.core.filters.Command import command
from configparser import ConfigParser
from kantex import md as Markdown
import logging


class Bot(Client):
    def __init__(self, name: str = 'scp-bot'):
        self.name = name
        super().__init__(
            name,
            workers=8,
        )

    async def start(self):
        await super().start()
        logging.warning('`Bot.Client` started.')

    async def stop(self, *args):
        await super().stop()
        logging.warning('`Bot.Client` stopped.')

    def command(self, *args, **kwargs):
        return command(*args, **kwargs)

        
    filters = filters
    types = types
    md = Markdown
    _config = ConfigParser()
    _config.read('config.ini')
    _sudo = []
    for x in _config.get('scp-5170', 'SudoList').split():
        _sudo.append(int(x))
    sudo = (filters.user(_sudo))