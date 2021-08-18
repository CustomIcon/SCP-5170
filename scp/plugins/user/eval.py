import traceback, sys
import os

from io import StringIO

from scp.utils.meval import meval
from scp import user



@user.on_message(user.filters.me & user.command('eval'))
async def eval(client: user, message: user.types.Message):
    try:
        cmd = message.text.split(' ', maxsplit=1)[1]
    except IndexError:
        await message.delete()
        return
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await meval(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ''
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = 'Success'
    out = str(user.md.KanTeXDocument(
        user.md.Section('Output:',
            user.md.Code(evaluation.strip()))
    ))
    if len(out) > 4096:
        filename = 'output.txt'
        with open(filename, 'w+', encoding='utf8') as out_file:
            out_file.write(str(evaluation.strip()))
        await message.reply_document(
            document=filename,
            quote=True
        )
        os.remove(filename)
    else:
        await message.reply(
            text=out,
            quote=True,
        )