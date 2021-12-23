from pyrogram import Client, filters, types, raw, errors, session, handlers
from scp.core.filters.Command import command
from configparser import ConfigParser
from kantex import md as Markdown
from aiohttp import ClientSession, client_exceptions
import asyncio
import logging


session.Session.notice_displayed = True


class client(Client):
    def __init__(
        self,
        name: str,
        aioclient=ClientSession,
    ):
        self.name = name
        super().__init__(
            self.name,
            workers=16,
            config_file='config.ini',
        )
        self.aioclient = aioclient()

    async def start(self):
        await super().start()
        logging.warning(
            f'logged in as {(await super().get_me()).first_name}.',
        )

    async def stop(self, *args):
        logging.warning(
            f'logged out from {(await super().get_me()).first_name}.',
        )
        await super().stop()

    def command(self, *args, **kwargs):
        return command(*args, **kwargs)

    async def send(
        self,
        data: raw.core.TLObject,
        retries: int = session.Session.MAX_RETRIES,
        timeout: float = session.Session.WAIT_TIMEOUT,
        sleep_threshold: float = None
    ):
        while True:
            try:
                return await super().send(
                    data=data,
                    retries=retries,
                    timeout=timeout,
                    sleep_threshold=sleep_threshold,
                )
            except (
                errors.SlowmodeWait,
                errors.FloodWait,
            ) as e:
                logging.warning(f"Sleeping for - {e.x} | {e}")
                await asyncio.sleep(e.x + 2)

    # from Kantek
    async def resolve_url(self, url: str) -> str:
        if not url.startswith('http'):
            url: str = f'http://{url}'
        async with self.aioclient.get(
            f'http://expandurl.com/api/v1/?url={url}',
        ) as response:
            e = await response.text()
        return e if e != 'false' and e[:-1] != url else None

    async def Request(self, url: str, type: str, *args, **kwargs):
        if type == 'get':
            resp = await self.aioclient.get(url, *args, **kwargs)
        elif type == 'post':
            resp = await self.aioclient.post(url, *args, **kwargs)
        elif type == 'put':
            resp = await self.aioclient.put(url, *args, **kwargs)
        try:
            return await resp.json()
        except client_exceptions.ContentTypeError:
            return (await resp.read()).decode('utf-8')

    async def netcat(
        self,
        host: str,
        port: int,
        content: str
    ):
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
    handlers = handlers
    md = Markdown
    exceptions = errors
    _config = ConfigParser()
    _config.read('config.ini')
    _sudo = []
    for x in _config.get('scp-5170', 'SudoList').split():
        _sudo.append(int(x))
    sudo = (filters.me | filters.user(_sudo))
    log_channel = _config.getint('scp-5170', 'LogChannel')
