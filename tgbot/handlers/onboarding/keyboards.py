from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from tgbot.handlers.onboarding.static_text import github_button_text


def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                github_button_text, url="https://github.com/sajadsj"
            ),
        ]
    ]

    return InlineKeyboardMarkup(buttons)
