import logging
import os
import sys
import time
from .core.clients import Bot, User

RUNTIME = time.time()
if sys.version_info[0] < 3 or sys.version_info[1] < 8:
    logging.error('Python version Lower than 3.8! Abort!')
    sys.exit()


if os.path.exists('scp/logs/logs.txt'):
    with open('scp/logs/logs.txt', 'a') as f:
        f.write('PEEK OF LOG FILE')
LOG_FORMAT = (
    '%(filename)s:%(lineno)s %(levelname)s: %(message)s'
)

logging.basicConfig(
    level=logging.ERROR,
    format=LOG_FORMAT,
    datefmt='%m-%d %H:%M',
    filename='scp/logs/logs.txt',
    filemode='w',
)
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter(LOG_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

log = logging.getLogger()

bot = Bot()
user = User()