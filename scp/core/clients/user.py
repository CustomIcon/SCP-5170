from pyrogram import Client, filters, types
from scp.core.filters.Command import command


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
    
    me = filters.me

    types = types