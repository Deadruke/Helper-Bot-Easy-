import os
import uuid

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)

from video.processor import process_video

router = Router()


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🎬 Мои видео",
                callback_data="my_videos"
            )],
            [InlineKeyboardButton(
                text="⚙️ Настройки",
                callback_data="settings"
            )],
            [InlineKeyboardButton(
                text="ℹ️ Помощь",
                callback_data="help"
            )],
        ]
    )


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Это твой личный видеоредактор.",
        reply_markup=main_menu()
    )


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Отправь своё видео, и я попробую обработать его."
    )


@router.callback_query(F.data == "my_videos")
async def my_videos(callback):
    await callback.answer()
    await callback.message.answer("История обработки появится позже.")


@router.callback_query(F.data == "settings")
async def settings(callback):
    await callback.answer()
    await callback.message.answer("Настройки скоро появятся.")


@router.callback_query(F.data == "help")
async def help_button(callback):
    await callback.answer()
    await callback.message.answer("Отправь видео в чат.")


@router.message(F.video)
async def receive_video(message: Message):
    os.makedirs("data", exist_ok=True)

    file_id = uuid.uuid4().hex
    input_path = f"data/{file_id}_input.mp4"
    output_path = f"data/{file_id}_output.mp4"

    await message.answer("⏳ Получил видео. Начинаю обработку...")

    try:
        await message.bot.download(
            message.video,
            destination=input_path
        )

        process_video(input_path, output_path)

        await message.answer_video(
            FSInputFile(output_path),
            caption="Готово! Видео обработано."
        )

    except Exception as error:
        await message.answer(
            f"Не удалось обработать видео: {str(error)[:500]}"
        )

    finally:
        for path in (input_path, output_path):
            if os.path.exists(path):
                os.remove(path)
