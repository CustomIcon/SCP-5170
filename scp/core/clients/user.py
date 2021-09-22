from distutils.log import error
from pyrogram import Client, filters, types, raw, errors
from scp.core.filters.Command import command
from configparser import ConfigParser
from kantex import md as Markdown
from aiohttp import ClientSession, client_exceptions
import asyncio
import logging
from typing import Union, List, Optional



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
        self.aioclient = aioclient()

    async def start(self):
        await super().start()
        logging.warning('`User.Client` started.')

    async def stop(self, *args):
        await super().stop()
        logging.warning('`Use.Client` started.')

    def command(self, *args, **kwargs):
        return command(*args, **kwargs)
    
    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = object,
        entities: List["types.MessageEntity"] = None,
        disable_web_page_preview: bool = None,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        schedule_date: int = None,
        reply_markup: Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ] = None
    ) -> "types.Message":
        try:
            return await super().send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                entities=entities,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                schedule_date=schedule_date,
                reply_markup=reply_markup
            )
        except errors.SlowmodeWait as e:
            await asyncio.sleep(e.x)
            return await super().send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                entities=entities,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                schedule_date=schedule_date,
                reply_markup=reply_markup
            )
        
    async def send_inline_bot_result(
        self,
        chat_id: Union[int, str],
        query_id: int,
        result_id: str,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        hide_via: bool = None
    ):
        try:
            return await super().send_inline_bot_result(
                chat_id=chat_id,
                query_id=query_id,
                result_id=result_id,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                hide_via=hide_via
            )
        except errors.SlowmodeWait as e:
            await asyncio.sleep(e.x)
            return await super().send_inline_bot_result(
                chat_id=chat_id,
                query_id=query_id,
                result_id=result_id,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                hide_via=hide_via
            )

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

    async def putRequest(
        self,
        *args,
        **kwargs
    ):
        async with self.aioclient.put(*args, **kwargs) as resp:
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
