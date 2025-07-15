import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.markdown import hbold
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import F

import asyncio
import logging
import aiohttp
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@HodlerUz"

if not TOKEN:
    raise SystemExit("🚨 BOT_TOKEN environment’da topilmadi.")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML, session=AiohttpSession())
dp = Dispatcher()

async def fetch_top_coins():
    url = "https://api.coinpaprika.com/v1/tickers?limit=10"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            text = f"{hbold('📊 TOP 10 kriptovalyutalar narxi')}\n\n"
            for coin in data[:10]:
                name = coin['name']
                symbol = coin['symbol']
                price = coin['quotes']['USD']['price']
                text += f"{symbol} ({name}): ${price:.2f}\n"
            text += "\n🌐 Top 100 coinlar ro'yxati: https://coinpaprika.com"
            return text

async def send_scheduled_message():
    while True:
        now = datetime.now()
        if now.hour in [8, 20] and now.minute == 0:
            try:
                msg = await fetch_top_coins()
                await bot.send_message(CHANNEL_ID, msg)
            except Exception as e:
                logging.error(f"Xatolik: {e}")
            await asyncio.sleep(60)
        await asyncio.sleep(30)

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("Bot faollashtirilgan. Kanalga avtomatik kurs yuboriladi.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(send_scheduled_message())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
