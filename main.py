#!/usr/bin/env pipenv run python
"""
Nonsense plurk bot

Distributed under terms of the WTFPL license.
"""

from pbot import Bot
from msg import gen_msg
import loguru

if __name__=="__main__":
    loguru.logger.add(
        'data/{time}.log',
        rotation='1 day',
        retention='7 days',
        enqueue=True,
        level='DEBUG')
    bot = Bot("token.txt", "data/users.db", gen_msg)
    bot.main()
