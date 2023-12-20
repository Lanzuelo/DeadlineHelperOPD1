import asyncio

import logging

import handlers

from models.databases import create_database

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot import dp, bot

# add logging
logging.basicConfig(level=logging.INFO)


# функция при запуске
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(handlers.every_minute_task, trigger='interval', seconds=60)
    scheduler.start()
    create_database()
    await dp.start_polling(bot)
    
    

if __name__ == "__main__":
    asyncio.run(main())