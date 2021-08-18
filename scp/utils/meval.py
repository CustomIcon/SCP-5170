async def meval(code, client, message):
    exec(
        'async def __aexec(client, message): '
        + ''.join(f'\n {a}' for a in code.split('\n')),
    )
    return await locals()['__aexec'](client, message)