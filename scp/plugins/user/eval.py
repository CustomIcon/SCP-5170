# https://greentreesnakes.readthedocs.io/
# https://gitlab.com/blankX/sukuinote/-/blob/master/sukuinote/plugins/pyexec.py
import ast
import sys
import html
import inspect
import asyncio
from shortuuid import ShortUUID
from io import StringIO, BytesIO
from scp import user

exec_tasks = dict()


@user.on_message(
    user.filters.me
    & user.filters.command('eval', prefixes=user._config.get('scp-5170', 'prefixes').split())
)
async def pyexec(client: user, message: user.types.Message):
    code = message.text.split(None, 1)[1]
    class UniqueExecReturnIdentifier:
        pass
    tree = ast.parse(code)
    obody = tree.body
    body = obody.copy()
    body.append(ast.Return(ast.Name('_ueri', ast.Load())))
    try:
        exx = _gf(body)
    except SyntaxError as ex:
        if ex.msg != "'return' with value in async generator":
            raise
        exx = _gf(obody)
    rnd_id = "#" + str(ShortUUID().random(length=5))
    reply = await message.reply_text(f'Executing <code>{rnd_id}</code>',quote=True)
    oasync_obj = exx(
        client,
        client,
        message,
        message,
        reply,
        message.reply_to_message,
        message.reply_to_message,
        UniqueExecReturnIdentifier
    )
    if inspect.isasyncgen(oasync_obj):
        async def async_obj():
            return [i async for i in oasync_obj]
    else:
        async def async_obj():
            to_return = [await oasync_obj]
            return [] if to_return == [UniqueExecReturnIdentifier] else to_return
    stdout = sys.stdout
    stderr = sys.stderr
    wrapped_stdout = StringIO()
    try:
        sys.stdout = sys.stderr = wrapped_stdout
        task = asyncio.create_task(async_obj())
        exec_tasks[rnd_id] = task
        try:
            returned = await task
        except Exception as err:
            returned = err
            return await reply.edit_text(
                user.md.KanTeXDocument(user.md.Section('Error:', user.md.Code(err)))
            )
    except asyncio.CancelledError:
        sys.stdout = stdout
        sys.stderr = stderr
        exec_tasks.pop(rnd_id, None)
        return await reply.edit_text('Cancelled')
    finally:
        sys.stdout = stdout
        sys.stderr = stderr
        exec_tasks.pop(rnd_id, None)
    wrapped_stdout.seek(0)
    output = ''
    wrapped_stdout_text = wrapped_stdout.read().strip()
    if wrapped_stdout_text:
        output += f'<code>{html.escape(wrapped_stdout_text)}</code>\n'
    for i in returned:
        output += f'<code>{html.escape(str(i).strip())}</code>\n'
    if not output.strip():
        output = 'Success'
    
    if len(output) > 4096:
        out = wrapped_stdout_text + "\n"
        for i in returned:
            out += str(i).strip() + "\n"
        f = BytesIO(out.strip().encode('utf-8'))
        f.name = "output.txt"
        await asyncio.gather(reply.delete(), message.reply_document(f))
    else:
        await reply.edit_text(
            user.md.KanTeXDocument(
                user.md.Section('Output:', user.md.Code(output))
            )
        )


@user.on_message(user.filters.me & user.command('listTask'))
async def listexec(_, message: user.types.Message):
    text = '\n'.join(map(str, exec_tasks))
    if len(text) > 4096:
        f = BytesIO(text.encode('utf-8'))
        f.name = 'exectasks.txt'
        await message.reply_document(f)
    else:
        text = '\n'.join(map(lambda i: f'- <code>{i}</code>', exec_tasks))
        await message.reply_text(text or 'No tasks', quote=True)


@user.on_message(user.filters.me & user.command('cancelTask'))
async def cancelexec(_, message: user.types.Message):
    try:
        task = exec_tasks.get(message.command[1])
    except IndexError:
        return
    if not task:
        return await message.reply_text('Task does not exist', quote=True)
    task.cancel()


def _gf(body):
    func = ast.AsyncFunctionDef(
        'ex',
        ast.arguments(
            [],
            [
                ast.arg(
                    i, None, None
                ) for i in [
                    'c',
                    'client',
                    'm',
                    'message',
                    'executing',
                    'r',
                    'reply',
                    '_ueri'
                ]
            ],
            None,
            [],
            [],
            None,
            []
        ),
        body,
        [],
        None,
        None
    )
    ast.fix_missing_locations(func)
    mod = ast.parse('')
    mod.body = [func]
    fl = locals().copy()
    exec(compile(mod, '<ast>', 'exec'), globals(), fl)
    return fl['ex']