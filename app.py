import config
import atexit
from loader import dp, bot, connect_db, logger
import time
import datetime
import asyncio


async def on_startup():
    config.START_TIME = time.time()
    await connect_db()
    logger.info('Bot online')
    await dp.start_polling(bot)


@atexit.register
def on_exit():
    _start_time = config.START_TIME
    cur_time = int(time.time())
    online_time_row = str(datetime.timedelta(seconds=cur_time - _start_time)).split(':')
    day_hours = 0
    if 'day' in online_time_row[0] or 'days' in online_time_row[0]:
        day_hours = int(online_time_row[0].split(' ')[0]) * 24
        online_time_row[0] = int(online_time_row[0].split(' ')[2])
    online_time_h = str(int(online_time_row[0]) + day_hours) + 'h ' if int(online_time_row[0]) != 0 else ''
    online_time_m = str(int(float(online_time_row[1]))) + 'm ' if float(online_time_row[1]) != 0 else ''
    online_time_s = str(int(float(online_time_row[2]))) + 's ' if float(online_time_row[2]) != 0 else ''
    logger.info(f'Bot offline. Online time: {online_time_h}{online_time_m}{online_time_s}')


if __name__ == "__main__":
    try:
        import handlers.users
        dp.include_router(handlers.users.router)
        asyncio.run(on_startup())
    except Exception as ex:
        logger.critical(f"critical error while bot polling (errmsg: {ex})", exc_info=True)
