from pyrogram import Client, filters, types
from scp.core.filters.Command import user_command as command
from configparser import ConfigParser
from kantex import md as Markdown


class User(Client):
    def __init__(self, name: str = 'scp-user'):
        self.name = name
        super().__init__(
            name,
            workers=8,
        )

    async def start(self):
        await super().start()
        print('User started. Hi.')

    async def stop(self, *args):
        await super().stop()
        print('User stopped. Bye.')
    
    def command(self, *args):
        return command(*args)

    filters = filters
    types = types
    md = Markdown
    _config = ConfigParser()
    _config.read('config.ini')
    sudo = []
    for x in _config.get('scp-5170', 'SudoList').split():
        sudo.append(int(x))