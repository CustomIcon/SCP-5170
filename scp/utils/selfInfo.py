from scp import user, bot

info = {}


async def updateInfo():
    global info
    u = await user.get_me()
    b = await bot.get_me()
    info['_user_id'] = u.id
    info['_user_username'] = u.username
    info['_bot_id'] = b.id
    info['_bot_username'] = b.username