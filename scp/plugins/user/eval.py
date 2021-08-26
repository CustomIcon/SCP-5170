# https://greentreesnakes.readthedocs.io/
# https://gitlab.com/blankX/sukuinote/-/blob/master/sukuinote/plugins/pyexec.py
import ast
import sys
import html
import inspect
import asyncio
from shortuuid import ShortUUID
from io import StringIO, BytesIO
from scp import user, bot
from pyrogram import errors
from scp.utils.selfInfo import info

exec_tasks = {}


@user.on_message(
    ~user.filters.forwarded
    & ~user.filters.sticker
    & ~user.filters.via_bot
    & ~user.filters.edited
    & user.filters.me
    & user.filters.command(
        'eval',
        prefixes=user._config.get('scp-5170', 'prefixes').split(),
    ),
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
    rnd_id = '#' + str(ShortUUID().random(length=5))
    reply = await message.reply_text(
        f'Executing <code>{rnd_id}</code>',
        quote=True,
    )
    oasync_obj = exx(
        client,
        client,
        message,
        message,
        reply,
        message.reply_to_message,
        message.reply_to_message,
        UniqueExecReturnIdentifier,
    )
    if inspect.isasyncgen(oasync_obj):
        async def async_obj():
            return [i async for i in oasync_obj]
    else:
        async def async_obj():
            to_return = [await oasync_obj]
            return [] if to_return == [
                UniqueExecReturnIdentifier,
            ] else to_return
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
                user.md.KanTeXDocument(
                    user.md.Section('Error:', user.md.Code(err)),
                ),
            )
    except asyncio.CancelledError:
        sys.stdout = stdout
        sys.stderr = stderr
        exec_tasks.pop(rnd_id, None)
        return await reply.edit_text(
            user.md.KanTeXDocument(
                user.md.Section(
                    'Task Cancelled:',
                    user.md.Code(f'{rnd_id} has been canceled.'),
                ),
            ),
        )
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
        out = wrapped_stdout_text + '\n'
        for i in returned:
            out += str(i).strip() + '\n'
        f = BytesIO(out.strip().encode('utf-8'))
        f.name = 'output.txt'
        await asyncio.gather(reply.delete(), message.reply_document(f))
    else:
        await reply.edit_text(
            user.md.KanTeXDocument(
                user.md.Section('Output:', user.md.Code(output)),
            ),
        )


@user.on_message(user.filters.me & user.command('listEval'))
async def listexec(_, message: user.types.Message):
    try:
        x = await user.get_inline_bot_results(
            info['_bot_username'],
            '_listEval',
        )
    except (
        errors.exceptions.bad_request_400.PeerIdInvalid,
        errors.exceptions.bad_request_400.BotResponseTimeout,
    ):
        return await message.reply('no tasks', quote=True)
    for m in x.results:
        await message.reply_inline_bot_result(x.query_id, m.id, quote=True)


@bot.on_inline_query(
    user.filters.user(info['_user_id'])
    & user.filters.regex('^_listEval'),
)
async def _(_, query: user.types.InlineQuery):
    buttons = [[
        user.types.InlineKeyboardButton(
            text='cancel all',
            callback_data='cancel_eval_all',
        ),
    ]]
    for x, _ in exec_tasks.items():
        buttons.append(
            [
                user.types.InlineKeyboardButton(
                    text=x, callback_data=f'cancel_eval_{x}',
                ),
            ],
        )
    await query.answer(
        results=[
            user.types.InlineQueryResultArticle(
                title='list eval tasks',
                input_message_content=user.types.InputTextMessageContent(
                    user.md.KanTeXDocument(
                        user.md.Section(
                            'ListEvalTasks',
                            user.md.KeyValueItem(
                                'Tasks Running',
                                str(len(exec_tasks)),
                            ),
                        ),
                    ),
                ),
                reply_markup=user.types.InlineKeyboardMarkup(buttons),
            ),
        ],
        cache_time=0,
    )


@bot.on_callback_query(
    user.filters.user(info['_user_id'])
    & user.filters.regex('^cancel_'),
)
async def cancelexec(_, query: user.types.CallbackQuery):
    Type = query.data.split('_')[1]
    taskID = query.data.split('_')[2]
    if Type == 'eval':
        if taskID == 'all':
            for _, i in exec_tasks.items():
                i.cancel()
            return await query.edit_message_text(
                'All tasks has been cancelled',
            )
        else:
            try:
                task = exec_tasks.get(taskID)
            except IndexError:
                return
        if not task:
            return await query.answer(
                'Task does not exist anymore',
                show_alert=True,
            )
        task.cancel()
        return await query.edit_message_text(f'{taskID} has been cancelled')


def _gf(body):
    func = ast.AsyncFunctionDef(
        'ex',
        ast.arguments(
            [],
            [
                ast.arg(
                    i, None, None,
                ) for i in [
                    'c',
                    'client',
                    'm',
                    'message',
                    'executing',
                    'r',
                    'reply',
                    '_ueri',
                ]
            ],
            None,
            [],
            [],
            None,
            [],
        ),
        body,
        [],
        None,
        None,
    )
    ast.fix_missing_locations(func)
    mod = ast.parse('')
    mod.body = [func]
    fl = locals().copy()
    exec(compile(mod, '<ast>', 'exec'), globals(), fl)
    return fl['ex']
