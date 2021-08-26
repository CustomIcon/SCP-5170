from pyrogram import Client, filters, types, raw
from scp.core.filters.Command import command
from configparser import ConfigParser
from kantex import md as Markdown
from aiohttp import ClientSession, ClientTimeout, client_exceptions
import asyncio
import logging


class User(Client):
    def __init__(
        self,
        name: str = 'scp-user',
        aioclient=ClientSession,
    ):
        self.name = name
        super().__init__(
            name,
            workers=8,
        )
        self.aioclient = aioclient(timeout=ClientTimeout(total=2))

    async def start(self):
        await super().start()
        logging.warning('`User.Client` started.')

    async def stop(self, *args):
        await super().stop()
        logging.warning('`Use.Client` started.')

    def command(self, *args, **kwargs):
        return command(*args, **kwargs)

    # from Kantek
    async def resolve_url(self, url: str) -> str:
        if not url.startswith('http'):
            url: str = f'http://{url}'
        async with self.aioclient.get(
            f'http://expandurl.com/api/v1/?url={url}',
        ) as response:
            e = await response.text()
        return e if e != 'false' and e[:-1] != url else None

    async def getRequest(self, url: str):
        async with self.aioclient.get(url) as resp:
            try:
                return await resp.json()
            except client_exceptions.ContentTypeError:
                return (await resp.read()).decode('utf-8')

    async def postRequest(
        self,
        *args,
        **kwargs
    ):
        async with self.aioclient.post(*args, **kwargs) as resp:
            try:
                return await resp.json()
            except client_exceptions.ContentTypeError:
                return (await resp.read()).decode('utf-8')

    async def netcat(self, host: str, port: int, content: str):
        reader, writer = await asyncio.open_connection(
            host, port,
        )
        writer.write(content.encode())
        await writer.drain()
        data = (await reader.read(100)).decode().strip('\n\x00')
        writer.close()
        await writer.wait_closed()
        return data

    filters = filters
    raw = raw
    types = types
    md = Markdown
    _config = ConfigParser()
    _config.read('config.ini')
    _sudo = []
    for x in _config.get('scp-5170', 'SudoList').split():
        _sudo.append(int(x))
    sudo = (filters.me | filters.user(_sudo))
    log_channel = _config.getint('scp-5170', 'LogChannel')
