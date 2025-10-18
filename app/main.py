import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import exceptions
from config import config
from handlers import router
from db import init_db
from tele_client import get_client, ensure_auth

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # Проверяем наличие токена бота
    if not config.BOT_TOKEN:
        logger.error('BOT_TOKEN не установлен. Заполните .env файл или переменные окружения.')
        return

    # Инициализируем базу данных
    init_db()

    # АВТОРИЗАЦИЯ TELEGRAM CLIENT
    print("🔐 Начинаем авторизацию Telethon клиента...")
    try:
        await ensure_auth()
        print("✅ Telethon клиент авторизован!")
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        return

    # Создаем объекты бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # start Telethon client session in background
    tele_client = get_client()

    try:
        logger.info('Запускаем бота...')
        await dp.start_polling(bot)
    except exceptions.TelegramAPIError:
        logger.error('Ошибка Telegram API')
    except exceptions.CancelledError:
        logger.info('Бот остановлен')
    except Exception as e:
        logger.error(f'Неожиданная ошибка: {e}')
    finally:
        # Корректно закрываем сессии
        await bot.session.close()
        await tele_client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())