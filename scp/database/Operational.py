import configparser
from scp import user


async def InitializeDatabase():
    try:
        user._config.getint(
            '.internal',
            'databaseChannel',
        )
    except configparser.NoSectionError:
        with open('config.ini', 'w') as file:
            user._config.add_section('.internal')
            channel = await user.create_channel(
                'scp-Database',
                description='Do not play with this channel!',
            )
            user._config.set(
                '.internal',
                'databaseChannel',
                str(channel.id),
            )
            user._config.write(file)
