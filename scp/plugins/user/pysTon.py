from pyston import PystonClient, exceptions
import os
from scp import user
import aiofiles
import time
from scp.utils.parser import HumanizeTime


__PLUGIN__ = 'piston'
__DOC__ = str(
    user.md.KanTeXDocument(
        user.md.Section(
            'Execute code in a safer Environment',
            user.md.SubSection(
                'Execute',
                user.md.Code(
                    '(*prefix)exec {language} {code_or_Document}',
                ),
            ),
            user.md.SubSection(
                'get supported Languages',
                user.md.Code('(*prefix)execLang'),
            ),
        ),
    ),
)


@user.on_message(
    user.sudo
    & user.filters.command(
        'exec',
        prefixes=user._config.get('scp-5170', 'prefixes').split(),
    ),
)
async def _(_, message: user.types.Message):
    client = PystonClient()
    try:
        arg = message.text.split(None, 1)[1].split(None, 1)
        language = arg[0]
        code = arg[1]
    except IndexError:
        if (
            not message.reply_to_message
            or not message.reply_to_message.document
        ):
            return
        file = await message.reply_to_message.download()
        try:
            language = message.text.split(None, 1)[1]
        except IndexError:
            language = 'python'
        async with aiofiles.open(file, 'r') as f:
            code = await f.read()
        os.remove(file)
    start = time.time()
    try:
        output = await client.execute(language, code)
    except exceptions.InvalidLanguage as err:
        output = err
    end = time.time()
    await client.close_session()
    return await message.reply(
        user.md.Section(
            'Evaluation',
            user.md.SubSection(
                'Output',
                user.md.Code(output),
            ),
            user.md.SubSection(
                'Language',
                user.md.Code(language),
            ),
            user.md.SubSection(
                'TimeTaken',
                user.md.Code(HumanizeTime(end - start)),
            ),

        ),
        quote=True,
    )


@user.on_message(
    user.sudo
    & user.command('execLang'),
)
async def _(_, message: user.types.Message):
    client = PystonClient()
    sec = user.md.Section('Languages')
    for language in await client.get_runtimes(formatted=False):
        sec.append(
            user.md.KeyValueItem(
                language['language'], language['version'],
            ),
        )
    await client.close_session()
    return await message.reply(sec, quote=True)
