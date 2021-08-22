from pyrogram import Client, filters, types, raw
from scp.core.filters.Command import user_command as command
from configparser import ConfigParser
from kantex import md as Markdown
from aiohttp import ClientSession, ClientTimeout, ClientError
from faker import Faker
import asyncio
import socket
from typing import Optional, Any
from yarl import URL


class User(Client):
    def __init__(
        self,
        name: str = 'scp-user',
        aioclient =  ClientSession
    ):
        self.name = name
        super().__init__(
            name,
            workers=8,
        )
        self.aioclient = aioclient(timeout=ClientTimeout(total=2))

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
        except (ClientError, asyncio.TimeoutError, socket.gaierror):
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


    async def postRequest(
        self,
        url:str,
        json: dict = None,
        data: Any = None
    ):
        if data:
            async with self.aioclient.post(url, data=data) as resp:
                return await resp.json()
        else:
            async with self.aioclient.post(url, json=json) as resp:
                return await resp.json()
    

    async def netcat(self, host: str, port: int, content: str):
        reader, writer = await asyncio.open_connection(
            host, port
        )
        writer.write(content.encode())
        await writer.drain()
        data = (await reader.read(100)).decode().strip("\n\x00")
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