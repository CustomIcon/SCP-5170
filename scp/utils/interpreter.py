from pyrogram.utils import ainput
from scp.utils.bprint import bprint as print


async def aexec(code):
    # Make an async function with the code and `exec` it
    exec(
        f'async def __ex(): ' +
        ''.join(f'\n {l}' for l in code.split('\n'))
    )

    # Get `__ex` from local variables, call it and return the result
    return await locals()['__ex']()


async def shell():
    while True:
        try:
            inp = await ainput('scp > ')
        except (EOFError):
            ...
        try:
            await aexec(inp)
        except UnboundLocalError:
            ...
        except BaseException as err:
            print(err)