from pyrogram import Client


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