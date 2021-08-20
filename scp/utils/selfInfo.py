import scp

info = {}


async def updateInfo():
    u = await scp.user.get_me()
    b = await scp.bot.get_me()
    info['_user_id'] = u.id
    info['_user_username'] = u.username
    info['_bot_id'] = b.id
    info['_bot_username'] = b.username