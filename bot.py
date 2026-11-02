import asyncio
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)
from aiogram.exceptions import TelegramBadRequest
# -----------------------------
# CONFIG
# -----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher()
# Временные настройки пользователей
user_settings = {}
# Папка для временных файлов
WORK_DIR = Path(tempfile.gettempdir()) / "personal_video_editor"
WORK_DIR.mkdir(parents=True, exist_ok=True)
MAX_LOCAL_FILE_SIZE = 19 * 1024 * 1024
# -----------------------------
# KEYBOARDS
# -----------------------------
def main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Мои клипы",
                    callback_data="clips"
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
def settings_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Вертикально 9:16",
                    callback_data="format_vertical"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🖥 Оригинальный формат",
                    callback_data="format_original"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬆️ Баннер сверху",
                    callback_data="position_top"
                ),
                InlineKeyboardButton(
                    text="⬇️ Баннер снизу",
                    callback_data="position_bottom"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="home"
                )
            ],
        ]
    )
def video_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 9:16",
                    callback_data="format_vertical"
                ),
                InlineKeyboardButton(
                    text="🖥 Оригинал",
                    callback_data="format_original"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✂️ Обработать видео",
                    callback_data="process_video"
                )
            ],
        ]
    )
# -----------------------------
# HELPERS
# -----------------------------
def get_settings(user_id: int):
    if user_id not in user_settings:
        user_settings[user_id] = {
            "format": "original",
            "position": "bottom",
            "video_path": None,
        }
    return user_settings[user_id]
def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None
def run_ffmpeg(input_path: Path, output_path: Path, video_format: str):
    if not ffmpeg_available():
        raise RuntimeError("FFmpeg не установлен.")
    if video_format == "vertical":
        video_filter = (
            "scale=720:1280:"
            "force_original_aspect_ratio=increase,"
            "crop=720:1280"
        )
    else:
        video_filter = "scale='min(1280,iw)':-2"
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", str(input_path),
        "-vf", video_filter,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "26",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_path),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr[-2000:] or "Неизвестная ошибка FFmpeg."
        )
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("FFmpeg не создал выходной файл.")
# -----------------------------
# COMMANDS
# -----------------------------
@dp.message(CommandStart())
async def start_handler(message: Message):
    get_settings(message.from_user.id)
    await message.answer(
        "🎬 Привет! Это твой личный видеоредактор.\n\n"
        "Отправь небольшой собственный или разрешённый "
        "к публикации клип, и мы подготовим его.\n\n"
        "Выбери действие:",
        reply_markup=main_keyboard(),
    )
@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "📖 Как пользоваться:\n\n"
        "1. Отправь боту видео.\n"
        "2. Выбери формат.\n"
        "3. Нажми «Обработать видео».\n\n"
        "Поддерживается вертикальный формат 9:16.\n"
        "Для первого теста используй небольшой MP4-файл."
    )
# -----------------------------
# VIDEO UPLOAD
# -----------------------------
@dp.message(F.video)
async def receive_video(message: Message):
    user_id = message.from_user.id
    settings = get_settings(user_id)
    video = message.video
    if video.file_size and video.file_size > MAX_LOCAL_FILE_SIZE:
        await message.answer(
            "⚠️ Для первого прототипа файл слишком большой.\n\n"
            "Пожалуйста, отправь тестовый ролик размером до 19 МБ. "
            "Позже можно подключить отдельное хранилище "
            "для больших видео."
        )
        return
    status = await message.answer("📥 Получаю видео...")
    try:
        file_info = await bot.get_file(video.file_id)
        file_path = file_info.file_path
        if not file_path:
            await status.edit_text("Не удалось получить файл из Telegram.")
            return
        suffix = Path(file_path).suffix or ".mp4"
        input_path = WORK_DIR / f"{user_id}_input{suffix}"
        await bot.download_file(file_path, destination=input_path)
        settings["video_path"] = str(input_path)
        await status.edit_text(
            "✅ Видео получено!\n\n"
            "Выбери формат и запусти обработку:",
            reply_markup=video_keyboard(),
        )
    except Exception:
        logger.exception("Ошибка получения видео")
        await status.edit_text(
            "❌ Не удалось получить видео. "
            "Попробуй отправить его ещё раз."
        )
# -----------------------------
# BUTTONS
# -----------------------------
@dp.callback_query(F.data == "home")
async def home_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🏠 Главное меню:",
        reply_markup=main_keyboard(),
    )
@dp.callback_query(F.data == "settings")
async def settings_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "⚙️ Настройки видео:",
        reply_markup=settings_keyboard(),
    )
@dp.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📖 Отправь видео боту, выбери формат и запусти обработку.\n\n"
        "Для первого теста используй небольшой MP4-файл.",
        reply_markup=main_keyboard(),
    )
@dp.callback_query(F.data == "clips")
async def clips_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🎬 Отправь сюда собственный или разрешённый "
        "к публикации видеоклип."
    )
@dp.callback_query(F.data.in_({"format_vertical", "format_original"}))
async def format_callback(callback: CallbackQuery):
    settings = get_settings(callback.from_user.id)
    if callback.data == "format_vertical":
        settings["format"] = "vertical"
        text = "📱 Выбран вертикальный формат 9:16."
    else:
        settings["format"] = "original"
        text = "🖥 Выбран исходный формат."
    await callback.answer(text)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=video_keyboard()
        )
    except TelegramBadRequest:
        pass
@dp.callback_query(F.data.in_({"position_top", "position_bottom"}))
async def position_callback(callback: CallbackQuery):
    settings = get_settings(callback.from_user.id)
    settings["position"] = (
        "top" if callback.data == "position_top" else "bottom"
    )
    position_text = (
        "сверху" if settings["position"] == "top" else "снизу"
    )
    await callback.answer(f"Расположение выбрано: {position_text}")
@dp.callback_query(F.data == "process_video")
async def process_video_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    settings = get_settings(user_id)
    input_value = settings.get("video_path")
    await callback.answer()
    if not input_value:
        await callback.message.answer(
            "Сначала отправь мне видео."
        )
        return
    input_path = Path(input_value)
    if not input_path.exists():
        settings["video_path"] = None
        await callback.message.answer(
            "Исходный файл больше не найден. Отправь видео повторно."
        )
        return
    output_path = WORK_DIR / f"{user_id}_output.mp4"
    status = await callback.message.answer(
        "⏳ Обрабатываю видео. Это может занять некоторое время..."
    )
    try:
        await asyncio.to_thread(
            run_ffmpeg,
            input_path,
            output_path,
            settings["format"],
        )
        if not output_path.exists():
            raise RuntimeError("Выходной файл не найден.")
        output_size = output_path.stat().st_size
        if output_size > 49 * 1024 * 1024:
            await status.edit_text(
                "⚠️ Видео обработано, но оно слишком большое "
                "для отправки через обычный Telegram Bot API.\n\n"
                "Нужна отдельная инфраструктура для передачи файла."
            )
            return
        await status.edit_text("✅ Готово! Отправляю видео...")
        await callback.message.answer_video(
            video=FSInputFile(output_path),
            caption="🎬 Твой обработанный клип",
        )
        await status.delete()
    except subprocess.TimeoutExpired:
        await status.edit_text(
            "⏱ Обработка заняла слишком много времени. "
            "Попробуй более короткий ролик."
        )
    except Exception:
        logger.exception("Ошибка обработки видео")
        await status.edit_text(
            "❌ Не получилось обработать видео. "
            "Проверь журнал ошибок Render."
        )
    finally:
        if output_path.exists():
            output_path.unlink(missing_ok=True)
        if input_path.exists():
            input_path.unlink(missing_ok=True)
        settings["video_path"] = None
# -----------------------------
# START BOT
# -----------------------------
async def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "Не найдена переменная окружения BOT_TOKEN."
        )
    if not ffmpeg_available():
        raise RuntimeError(
            "FFmpeg не установлен или не найден в PATH."
        )
    logger.info("Бот запущен.")
    await dp.start_polling(bot)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        if bot:
            asyncio.run(bot.session.close())
