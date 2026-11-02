from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


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


def settings_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Вертикальный формат",
                    callback_data="format_vertical"
                )
            ],
            [
                InlineKeyboardButton(
                    text="↩️ Назад",
                    callback_data="back"
                )
            ],
        ]
    )
