from aiogram import Bot, Dispatcher

from config import BOT_TOKEN

# init bot
bot = Bot(token=BOT_TOKEN, parse_mode='html')
# Диспетчер
dp = Dispatcher() 
