# to the guy who stole my foreskin
from time import time
from collections import defaultdict
from typing import Union

USERS = defaultdict(list)
MESSAGES = 4
SECONDS = 6


def is_flood(uid: int) -> Union[bool, None]:
    """Checks if a user is flooding"""
    USERS[uid].append(time())
    if len(list(filter(lambda x: time() - int(x) < SECONDS, USERS[uid]))) > MESSAGES:
        return True