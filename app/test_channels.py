import asyncio
import sys
import os

sys.path.append(os.path.dirname(__file__))

from tele_client import fetch_latest_from_channel


async def test_channels():
    channels = ['@durov', '@telegram']

    for channel in channels:
        print(f"🔍 Проверяем канал: {channel}")
        messages = await fetch_latest_from_channel(channel, limit=2)
        if messages:
            print(f"✅ Успешно! Получено {len(messages)} сообщений")
            for msg in messages:
                print(f"   - ID: {msg['msg_id']}, Текст: {msg['text'][:50]}...")
        else:
            print(f"❌ Не удалось получить сообщения из {channel}")
        print()


if __name__ == "__main__":
    asyncio.run(test_channels())