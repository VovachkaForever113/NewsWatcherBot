from html import escape
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# Максимальная длина превью сообщения
MAX_PREVIEW = 400


def clean_html_tags(text: str) -> str:
    """Удаляет HTML теги из текста"""
    if not text:
        return ""

    # Удаляем простые HTML теги
    clean_text = re.sub(r'<[^>]+>', '', text)

    # Заменяем HTML сущности
    clean_text = clean_text.replace('&nbsp;', ' ') \
        .replace('&amp;', '&') \
        .replace('&lt;', '<') \
        .replace('&gt;', '>') \
        .replace('&quot;', '"') \
        .replace('&#39;', "'")

    return clean_text.strip()


def format_date(date_str: str) -> str:
    """Форматирует дату в читаемый вид"""
    try:
        # Парсим дату из строки
        if '+' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(date_str)

        # Форматируем в удобный вид
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return date_str.split('+')[0] if '+' in date_str else date_str


def render_message_preview(msg: dict) -> str:
    """
    Форматирует сообщение для отправки в Telegram с HTML разметкой

    Args:
        msg: Словарь с данными сообщения

    Returns:
        str: Отформатированная строка с HTML разметкой
    """
    try:
        # Получаем ID сообщения
        msg_id = msg.get('msg_id', 'N/A')

        # Получаем текст сообщения и очищаем от HTML тегов
        raw_text = msg.get('text', '').strip()
        if not raw_text:
            text = "📄 Сообщение без текста"
        else:
            text = clean_html_tags(raw_text)

        # Обрезаем текст если он слишком длинный
        if len(text) > MAX_PREVIEW:
            text = text[:MAX_PREVIEW] + '...'

        # Экранируем специальные символы для безопасности
        safe_text = escape(text)

        # Форматируем дату
        date = format_date(msg.get('date', 'Неизвестно'))

        # Создаем отформатированное сообщение
        return f"<b>#{msg_id}</b>\n{safe_text}\n<em>{date}</em>"

    except Exception as e:
        logger.error(f"Ошибка при форматировании сообщения: {e}")
        return "<b>Ошибка при загрузке сообщения</b>"


def render_message_with_media(msg: dict) -> str:
    """Расширенная версия с поддержкой медиа"""
    try:
        base_text = render_message_preview(msg)

        # Добавляем информацию о медиа если есть
        media_type = msg.get('media_type', '')
        if media_type:
            return f"{base_text}\n\n<code>{media_type}</code>"

        return base_text

    except Exception as e:
        logger.error(f"Ошибка при форматировании сообщения с медиа: {e}")
        return "<b>Ошибка при загрузке сообщения</b>"