from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

router = Router()


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Мои видео",
                    callback_data="my_videos"
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


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Это твой личный видеоредактор.\n\n"
        "Отправь своё видео или выбери действие в меню.",
        reply_markup=main_menu()
    )


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Как пользоваться:\n"
        "1. Отправь своё видео.\n"
        "2. Выбери нужные настройки.\n"
        "3. Дождись обработки."
    )


@router.callback_query(F.data == "my_videos")
async def my_videos(callback):
    await callback.answer()
    await callback.message.answer("Пока обработанных видео нет.")


@router.callback_query(F.data == "settings")
async def settings(callback):
    await callback.answer()
    await callback.message.answer(
        "Настройки редактора скоро появятся."
    )


@router.callback_query(F.data == "help")
async def help_button(callback):
    await callback.answer()
    await callback.message.answer(
        "Отправь своё видео в чат, чтобы начать."
    )


@router.message(F.video)
async def receive_video(message: Message):
    await message.answer(
        "Видео получил! Пока доступен только приём файлов. "
        "Обработку добавим отдельно."
    )
