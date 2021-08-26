import asyncio
from pyrogram import idle
from scp import user, bot
from scp.core.functions.plugins import loadUserPlugins, loadBotPlugins
from scp.utils.selfInfo import updateInfo
from scp.utils.interpreter import shell


HELP_COMMANDS = {}

loop = asyncio.get_event_loop()


async def start_bot():
    await bot.start()
    await user.start()
    await updateInfo()
    asyncio.create_task(shell())
    await asyncio.gather(
        loadBotPlugins(),
        loadUserPlugins(),
        idle()
    )


if __name__ == '__main__':
    loop.run_until_complete(start_bot())