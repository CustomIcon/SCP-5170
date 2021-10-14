import configparser
from scp import user
import ujson as json


async def checkTable(name: str):
    try:
        tableID = user._config.getint('.internal', name)
    except configparser.NoOptionError:
        table = await user.send_message(
            user._config.getint(
                '.internal',
                'databaseChannel'
            ),
            "{}"
        )
        user._config.set(
            '.internal',
            name,
            str(table.message_id)
        )
        with open('config.ini', 'w') as file:
            user._config.write(file)
        tableID = table.message_id
    return tableID



