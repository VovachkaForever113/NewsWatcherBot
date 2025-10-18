from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import config
from tele_client import fetch_latest_from_channel
from db import save_messages, get_latest
from templates import render_message_preview
from utils import parse_channel_list

router = Router()


def channels_keyboard(channels):
    """Создает клавиатуру со списком каналов"""
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=ch, callback_data=f"ch:{ch}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    text = (
        "<b>NewsWatcherBot</b>\n"
        "Выберите канал из списка, чтобы получить последние посты.\n"
        "Команды: /channels - список каналов, /refresh - обновить кэш"
    )
    channels = parse_channel_list(config.DEFAULT_CHANNELS)
    kb = channels_keyboard(channels)
    await message.answer(text, reply_markup=kb, parse_mode='HTML')


@router.message(Command('channels'))
async def cmd_channels(message: types.Message):
    """Обработчик команды /channels - показывает список каналов"""
    channels = parse_channel_list(config.DEFAULT_CHANNELS)
    if not channels:
        await message.answer('Список каналов пуст. Добавьте DEFAULT_CHANNELS в .env')
        return
    kb = channels_keyboard(channels)
    await message.answer('Выберите канал:', reply_markup=kb)


@router.message(Command('refresh'))
async def cmd_refresh(message: types.Message):
    """Обработчик команды /refresh - обновляет кэш всех каналов"""
    channels = parse_channel_list(config.DEFAULT_CHANNELS)
    await message.answer('Обновляю кэш каналов...')

    for ch in channels:
        messages = await fetch_latest_from_channel(ch, limit=config.PAGE_SIZE)
        save_messages(ch, messages)

    await message.answer('Готово. Используйте /channels чтобы посмотреть')


@router.callback_query(lambda c: c.data and c.data.startswith('ch:'))
async def cb_channel(query: types.CallbackQuery):
    """Обработчик нажатия на канал в клавиатуре"""
    try:
        channel = query.data.split(':', 1)[1]

        # Показываем сообщение о загрузке
        await query.message.edit_text(f'Загружаю последние {config.PAGE_SIZE} постов из {channel}...')

        # Пытаемся получить свежие сообщения
        messages = await fetch_latest_from_channel(channel, limit=config.PAGE_SIZE)

        if messages:
            # Сохраняем в базу и показываем
            save_messages(channel, messages)
            for m in messages:
                text = render_message_preview(m)
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Обновить', callback_data=f'refresh:{channel}')]
                ])
                await query.message.answer(text, parse_mode='HTML', reply_markup=kb)
        else:
            # Если не получилось - показываем кэш
            cached = get_latest(channel, limit=config.PAGE_SIZE)
            if cached:
                await query.message.answer('Не получилось достать напрямую — показываю кэш:')
                for m in cached:
                    await query.message.answer(render_message_preview(m), parse_mode='HTML')
            else:
                await query.message.answer('Не удалось получить сообщения из канала.')

    except Exception as e:
        await query.message.answer('Произошла ошибка при загрузке сообщений.')


@router.callback_query(lambda c: c.data and c.data.startswith('refresh:'))
async def cb_refresh(query: types.CallbackQuery):
    """Обработчик кнопки 'Обновить' для конкретного канала"""
    try:
        channel = query.data.split(':', 1)[1]

        # Показываем уведомление о обновлении
        await query.answer('Обновляю...')

        # Получаем свежие сообщения
        messages = await fetch_latest_from_channel(channel, limit=config.PAGE_SIZE)

        if messages:
            save_messages(channel, messages)
            await query.message.answer('Обновлено — вот последние посты:')
            for m in messages:
                text = render_message_preview(m)
                await query.message.answer(text, parse_mode='HTML')
        else:
            await query.message.answer('Не удалось обновить. Возможно канал приватный или неверный.')

    except Exception as e:
        await query.message.answer('Произошла ошибка при обновлении сообщений.')