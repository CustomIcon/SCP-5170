# to the guy who stole my foreskin
from time import time
from collections import defaultdict
from typing import Union
from pyrogram import types
import asyncio


USERS = defaultdict(list)
MESSAGES = 5
SECONDS = 6


async def is_flood(
    user: types.User,
    messages: int = MESSAGES,
    seconds: int = SECONDS,
    users: defaultdict = USERS,
) -> Union[bool, None]:
    """Checks if a user is flooding"""
    users[user.id].append(time())
    check = list(filter(lambda x: time() - int(x) < seconds, users[user.id]))
    if len(check) > messages:
        users[user.id] = check
        return True


async def cleaner(
    users: defaultdict = USERS,
    sleep: float = 30,
    seconds: int = SECONDS,
):
    while not await asyncio.sleep(sleep):
        for user, _ in users.copy().items():
            check = list(
                filter(lambda x: time() - int(x) < seconds, users[user]),
            )
            if not check:
                del users[user]
