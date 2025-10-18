import asyncio
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, ChannelInvalidError, SessionPasswordNeededError
from telethon.tl.types import Message
import logging
from config import config

logger = logging.getLogger(__name__)
_client = None


def get_client():
    """Создает и возвращает Telethon клиент (синглтон)"""
    global _client
    if _client is None:
        _client = TelegramClient(
            'newswatcher_session',
            config.TG_API_ID,
            config.TG_API_HASH
        )
    return _client


async def ensure_auth():
    """Убеждается что клиент авторизован"""
    client = get_client()
    if not client.is_connected():
        await client.connect()

    # Проверяем авторизацию
    if not await client.is_user_authorized():
        print("❌ Telethon клиент не авторизован!")
        print("📱 Откройте Telegram на телефоне для авторизации...")

        # Запрашиваем номер телефона если не указан в конфиге
        phone = getattr(config, 'TG_API_PHONE', None)
        if not phone:
            phone = input("Введите номер телефона (с кодом страны): ")

        await client.send_code_request(phone)
        code = input("Введите код из Telegram: ")
        try:
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            password = input("Введите пароль 2FA: ")
            await client.sign_in(password=password)
        print("✅ Авторизация успешна!")
    return client


async def check_connection():
    """Проверяет подключение к Telegram"""
    try:
        client = get_client()
        if not client.is_connected():
            await client.connect()

        # Проверяем авторизацию
        if not await client.is_user_authorized():
            return False, "Клиент не авторизован. Запустите бота из консоли для авторизации."

        # Проверяем что можем получить информацию о себе
        me = await client.get_me()
        return True, f"Подключено как: {me.username or me.first_name}"

    except Exception as e:
        return False, f"Ошибка подключения: {e}"


async def fetch_latest_from_channel(channel: str, limit: int = 5):
    """Получает последние сообщения из канала Telegram"""
    try:
        client = get_client()

        # Подключаемся если соединение не установлено
        if not client.is_connected():
            await client.connect()

        results = []
        async for msg in client.iter_messages(channel, limit=limit):
            if isinstance(msg, Message):
                text = msg.message or ''
                media_type = ""
                if msg.media:
                    if hasattr(msg.media, 'document'):
                        media_type = "📎 Файл"
                    elif hasattr(msg.media, 'photo'):
                        media_type = "🖼️ Фото"
                    elif hasattr(msg.media, 'webpage'):
                        media_type = "🌐 Ссылка"

                results.append({
                    'msg_id': msg.id,
                    'text': text,
                    'date': str(msg.date),
                    'media_type': media_type
                })

        logger.info(f"Получено {len(results)} сообщений из канала {channel}")
        return results

    except ChannelPrivateError:
        logger.error(f"Канал {channel} приватный или нет доступа")
        return []
    except ChannelInvalidError:
        logger.error(f"Неверный канал: {channel}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при получении сообщений из {channel}: {e}")
        return []


async def disconnect():
    """Корректно закрывает соединение"""
    global _client
    if _client and _client.is_connected():
        await _client.disconnect()
        _client = None
        logger.info("Соединение с Telegram закрыто")


def fetch_sync(channel: str, limit: int = 5):
    """Синхронная обертка для получения сообщений"""
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            fetch_latest_from_channel(channel, limit)
        )
    except Exception as e:
        logger.error(f"Ошибка в синхронном вызове для канала {channel}: {e}")
        return []