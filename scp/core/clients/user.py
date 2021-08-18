from pyrogram import Client, filters, types
from scp.core.filters.Command import user_command as command
from configparser import ConfigParser
from kantex import md as Markdown
from aiohttp import ClientSession, ClientTimeout, ClientError
from faker import Faker
import asyncio
import socket
from typing import Optional
from yarl import URL


class User(Client):
    def __init__(
        self,
        name: str = 'scp-user',
        aioclient: ClientSession = None
    ):
        self.name = name
        super().__init__(
            name,
            workers=8,
        )
        self.aioclient = ClientSession(timeout=ClientTimeout(total=2))

    async def start(self):
        await super().start()
        print('User started. Hi.')

    async def stop(self, *args):
        await super().stop()
        print('User stopped. Bye.')
    
    def command(self, *args):
        return command(*args)
    
    # from Kantek
    async def resolve_url(self, url: str, base_domain: bool = True) -> str:
        faker = Faker()
        headers = {'User-Agent': faker.user_agent()}
        old_url = url
        if not url.startswith('http'):
            url: str = f'http://{url}'
        try:
            async with self.aioclient.get(url, headers=headers) as response:
                url: URL = response.url
        except (ClientError, asyncio.TimeoutError, socket.gaierror) as err:
            return old_url

        if base_domain:
            url: Optional[str] = url.host
            _base_domain = url.split('.', maxsplit=url.count('.') - 1)[-1]
            if _base_domain:
                url: str = _base_domain
        return str(url)
    
    async def getRequest(self, url:str):
        async with self.aioclient.get(url) as resp:
            return await resp.json()


    

    filters = filters
    types = types
    md = Markdown
    _config = ConfigParser()
    _config.read('config.ini')
    sudo = []
    for x in _config.get('scp-5170', 'SudoList').split():
        sudo.append(int(x))