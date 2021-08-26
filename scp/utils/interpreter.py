from http import client
from pyrogram.utils import ainput
from scp.utils.bprint import bprint as print
from scp import user, bot


async def aexec(code, user, bot):
    # Make an async function with the code and `exec` it
    exec(
        f'async def __ex(user, bot): ' +
        ''.join(f'\n {l}' for l in code.split('\n'))
    )
    # Get `__ex` from local variables, call it and return the result
    return await locals()['__ex'](user, bot)


async def shell():
    while True:
        try:
            inp = await ainput('scp > ')
        except (EOFError):
            ...
        try:
            await aexec(inp, user, bot)
        except (UnboundLocalError, SyntaxError, SystemExit):
            ...
        except Exception as err:
            print(err)