import json
import logging
import logging.config
import config


logging.config.dictConfig(config.LOGGING_SETUP)
logging.basicConfig(format=u'[%(asctime)s][%(levelname)s] ::: %(filename)s(%(lineno)d) -> %(message)s',
                    level="INFO", filename='logs/bot.log')
logger = logging.getLogger('logger')


try:
    import asyncio
    import sys
    import os
    import atexit

    from aiogram import Bot, Dispatcher, Router, types
    from aiogram.enums import ParseMode
    from aiogram.utils.markdown import hbold
    from aiogram.filters import CommandStart
    from aiogram.types import Message
    from aiogram.fsm.storage.memory import MemoryStorage

    import time
    import datetime

    import pdb
    from config import DB_INFO
    import asyncpg as apg
except Exception as ex:
    logger.error("Ошибка при загрузке модулей. Попробуйте 'pip3 install -r requirements.txt' для установки "
                 "необходимых зависимостей. (errmsg:" + str(ex) + ")", exc_info=True)
    os._exit(1)


TOKEN = config.TOKEN
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


with open('logs/bot.log', 'a') as log:
    log.write(f'=============================\nNew bot session\n[{datetime.datetime.now()}]\n=============================\n')
with open('logs/err_bot.log', 'a') as log:
    log.write(f'=============================\nNew bot session\n[{datetime.datetime.now()}]\n=============================\n')


async def connect_db():
    try:
        await db.connect()
        await db.check_db_structure()
    except Exception as ex:
        logger.error("error while connecting to bot db. (errmsg:" + str(ex) + ")", exc_info=True)
        os._exit(2)


try:
    db = pdb.PostSQLDB(DB_INFO[0], DB_INFO[1], DB_INFO[2], DB_INFO[3])
except Exception as ex:
    logger.error("error while connecting to bot db. (errmsg:" + str(ex) + ")", exc_info=True)
    os._exit(2)
