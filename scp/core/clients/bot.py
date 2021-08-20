from pyrogram import Client, filters, types
from scp.core.filters.Command import bot_command as command
from configparser import ConfigParser


class Bot(Client):
    def __init__(self, name: str = 'scp-bot'):
        self.name = name
        super().__init__(
            name,
            workers=8,
        )

    async def start(self):
        await super().start()
        print('bot started. Hi.')

    async def stop(self, *args):
        await super().stop()
        print('bot stopped. Bye.')

    def command(self, *args):
        return command(*args)

        
    filters = filters
    types = types
    _config = ConfigParser()
    _config.read('config.ini')
    _sudo = []
    for x in _config.get('scp-5170', 'SudoList').split():
        _sudo.append(int(x))
    sudo = (filters.user(_sudo))