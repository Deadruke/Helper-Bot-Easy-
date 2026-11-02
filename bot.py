import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN в Render!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_settings = {}


def get_settings(user_id):
    if user_id not in user_settings:
        user_settings[user_id] = {
            "format": "vertical",
            "position": "bottom",
            "interval": 30,
        }
    return user_settings[user_id]


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Мои видео",
                    callback_data="videos"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Настройки",
                    callback_data="settings"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Помощь",
                    callback_data="help"
                )
            ],
        ]
    )


def settings_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Вертикальный 9:16",
                    callback_data="vertical"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🖥 Оригинальный формат",
                    callback_data="original"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬆️ Сверху",
                    callback_data="top"
                ),
                InlineKeyboardButton(
                    text="⬇️ Снизу",
                    callback_data="bottom"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔁 Каждые 30 секунд",
                    callback_data="interval_30"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔁 Каждую минуту",
                    callback_data="interval_60"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="home"
                )
            ],
        ]
    )


@dp.message(CommandStart())
async def start(message: Message):
    get_settings(message.from_user.id)

    await message.answer(
        "Привет! 🎬\n\n"
        "Это твой личный редактор CS2-клипов.\n\n"
        "Отправь собственное видео или выбери настройки.",
        reply_markup=main_menu()
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "📖 Как пользоваться:\n\n"
        "1. Отправь видео.\n"
        "2. Выбери настройки.\n"
        "3. Подготовь клип.\n\n"
        "Пока доступна базовая версия."
    )


@dp.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_text(
        "⚙️ Настройки видеоредактора:",
        reply_markup=settings_menu()
    )


@dp.callback_query(F.data == "home")
async def home(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_text(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "videos")
async def videos(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "🎬 Отправь своё видео в формате MP4."
    )


@dp.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "ℹ️ Бот предназначен для подготовки "
        "собственных и разрешённых к публикации видео."
    )


@dp.callback_query(F.data.in_({
    "vertical", "original", "top", "bottom",
    "interval_30", "interval_60"
}))
async def change_settings(callback: CallbackQuery):
    settings = get_settings(callback.from_user.id)

    options = {
        "vertical": ("format", "vertical", "Выбран формат 9:16"),
        "original": ("format", "original", "Выбран исходный формат"),
        "top": ("position", "top", "Выбрано расположение сверху"),
        "bottom": ("position", "bottom", "Выбрано расположение снизу"),
        "interval_30": ("interval", 30, "Интервал: 30 секунд"),
        "interval_60": ("interval", 60, "Интервал: 60 секунд"),
    }

    key, value, response = options[callback.data]
    settings[key] = value

    await callback.answer(response)


@dp.message(F.video)
async def receive_video(message: Message):
    size = message.video.file_size or 0

    await message.answer(
        "✅ Видео получено!\n\n"
        f"Размер: {size / (1024 * 1024):.1f} МБ\n\n"
        "Следующий этап — подключение видеопроцессора."
    )


@dp.message()
async def unknown_message(message: Message):
    await message.answer(
        "Отправь видео или воспользуйся кнопками меню.",
        reply_markup=main_menu()
    )


async def main():
    logger.info("Telegram-бот запускается...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        asyncio.run(bot.session.close())
