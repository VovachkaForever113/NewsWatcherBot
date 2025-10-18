import logging
from typing import List
from config import config

logger = logging.getLogger(__name__)

def parse_channel_list(raw: str) -> List[str]:
    """
    Парсит строку с каналами, разделенными запятыми, в список

    Args:
        raw: Сырая строка с каналами через запятую

    Returns:
        List[str]: Список очищенных каналов
    """
    try:
        # Проверяем на None и пустую строку
        if not raw or not raw.strip():
            logger.warning("Получена пустая строка для парсинга каналов")
            return []

        # Разделяем по запятым, убираем пробелы и фильтруем пустые значения
        channels = [channel.strip() for channel in raw.split(',')]
        channels = [channel for channel in channels if channel]

        logger.info(f"Успешно распаршено {len(channels)} каналов")
        return channels

    except Exception as e:
        logger.error(f"Ошибка при парсинге списка каналов: {e}")
        return []

def validate_channel_format(channels: List[str]) -> List[str]:
    """
    Проверяет и нормализует формат каналов

    Args:
        channels: Список каналов для проверки

    Returns:
        List[str]: Список валидных каналов
    """
    valid_channels = []

    for channel in channels:
        # Убираем лишние пробелы
        channel = channel.strip()

        # Пропускаем пустые строки
        if not channel:
            continue

        # Проверяем базовые форматы каналов
        if (channel.startswith('@') or
            channel.startswith('https://t.me/') or
            channel.isdigit() or
            channel.startswith('-100')):  # Для ID каналов
            valid_channels.append(channel)
        else:
            logger.warning(f"Неизвестный формат канала: {channel}")

    return valid_channels

def get_channels_from_config() -> List[str]:
    """
    Получает и парсит каналы из конфигурации

    Returns:
        List[str]: Список каналов из конфига
    """
    try:
        raw_channels = config.DEFAULT_CHANNELS
        channels = parse_channel_list(raw_channels)
        valid_channels = validate_channel_format(channels)

        logger.info(f"Загружено {len(valid_channels)} каналов из конфигурации")
        return valid_channels

    except AttributeError:
        logger.error("DEFAULT_CHANNELS не найден в конфигурации")
        return []
    except Exception as e:
        logger.error(f"Ошибка при получении каналов из конфига: {e}")
        return []