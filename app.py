import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from config import TOKEN

bot = Bot(token=TOKEN)

dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("Это работает")



@dp.message()
async def start_command(message: types.Message):
    await message.answer(message.text)




async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



asyncio.run(main())