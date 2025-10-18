import sqlite3
import logging
from typing import List, Dict, Any
from config import config

# Настройка логирования
logger = logging.getLogger(__name__)

# Путь к базе данных из конфига
DB = config.DB_PATH

# SQL для создания таблицы сообщений
CREATE_SQL = '''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT NOT NULL,
    msg_id INTEGER NOT NULL,
    text TEXT,
    date TEXT,
    UNIQUE(channel, msg_id)
);
'''


def init_db():
    """Инициализация базы данных - создает таблицы если их нет"""
    try:
        with sqlite3.connect(DB) as conn:
            cur = conn.cursor()
            cur.execute(CREATE_SQL)
            conn.commit()
            logger.info("База данных успешно инициализирована")
    except sqlite3.Error as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        raise


def save_messages(channel: str, messages: List[Dict[str, Any]]):
    """Сохраняет сообщения в базу данных"""
    if not messages:
        return

    try:
        with sqlite3.connect(DB) as conn:
            cur = conn.cursor()
            for m in messages:
                try:
                    cur.execute(
                        'INSERT OR IGNORE INTO messages (channel, msg_id, text, date) VALUES (?, ?, ?, ?)',
                        (channel, m.get('msg_id'), m.get('text'), m.get('date'))
                    )
                except sqlite3.Error as e:
                    logger.error(f"Ошибка сохранения сообщения {m.get('msg_id')}: {e}")
            conn.commit()
            logger.info(f"Сохранено {len(messages)} сообщений для канала {channel}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")


def get_latest(channel: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Получает последние сообщения из канала"""
    try:
        with sqlite3.connect(DB) as conn:
            cur = conn.cursor()
            cur.execute(
                'SELECT msg_id, text, date FROM messages WHERE channel=? ORDER BY msg_id DESC LIMIT ?',
                (channel, limit)
            )
            rows = cur.fetchall()
            return [{'msg_id': r[0], 'text': r[1], 'date': r[2]} for r in rows]
    except sqlite3.Error as e:
        logger.error(f"Ошибка получения сообщений для канала {channel}: {e}")
        return []