"""
    Telegram event handlers
"""
import logging
import os
import sys
from typing import Dict

import telegram.error
from django.views.decorators.csrf import csrf_exempt
from dtb.settings import (
    ADDRESS,
    COLOR,
    COUNT,
    DEBUG,
    DEL,
    DELETE_INFO,
    DETAILS,
    INFO,
    LOOP,
    PAY,
    PHONE,
    POLL,
    PRICE,
    RECEIPT,
    SALES_LINK,
    SIZE,
    TELEGRAM_TOKEN,
)
from telegram import Bot, BotCommand, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Dispatcher,
    Filters,
    MessageHandler,
    PicklePersistence,
    PollAnswerHandler,
    Updater,
)

from tgbot.handlers.onboarding import (
    commad_payment,
    command_info,
    command_item,
    followup,
)
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.utils import error, files


# add info handler
def setup_dispatcher(dp):
    # Follow up handler
    dp.add_handler(CommandHandler("followup", followup.my_order))
    # peyment handler
    peyment_conversation = ConversationHandler(
        name="peyment",
        entry_points=[CommandHandler("peyment_check", commad_payment.check)],
        states={
            RECEIPT: [
                MessageHandler(
                    Filters.photo & ~Filters.command,
                    commad_payment.photo_handler,
                )
            ],
            POLL: [
                MessageHandler(
                    Filters.regex("^Verify")
                    | Filters.regex("^Reject") & ~Filters.command,
                    commad_payment.poll,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", command_info.cancel_info)],
        allow_reentry=True,
        run_async=False,
        persistent=True,
    )
    dp.add_handler(peyment_conversation)
    add_info_coversation = ConversationHandler(
        name="add_info",
        entry_points=[
            CommandHandler("add_info", command_info.command_add_info)
        ],
        states={
            ADDRESS: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    command_info.add_address,
                )
            ],
            PHONE: [
                MessageHandler(
                    Filters.contact & ~Filters.command,
                    command_info.add_phone,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", command_info.cancel_info)],
        allow_reentry=True,
        run_async=False,
        persistent=True,
    )
    dp.add_handler(add_info_coversation)
    dp.add_handler(
        CommandHandler("delete_info", command_info.command_del_info)
    )

    # start handler
    dp.add_handler(CommandHandler("start", onboarding_handlers.command_start))

    # add item handler
    add_item_conversation = ConversationHandler(
        name="add_item",
        entry_points=[
            CommandHandler("add_item", command_item.command_add_item)
        ],
        states={
            SALES_LINK: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    command_item.add_sales_link,
                )
            ],
            PRICE: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    command_item.add_price,
                )
            ],
            COUNT: [
                MessageHandler(
                    Filters.regex("^[0-9]*$") & ~Filters.command,
                    command_item.add_count,
                )
            ],
            SIZE: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    command_item.add_size,
                )
            ],
            COLOR: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    command_item.add_color,
                )
            ],
            DETAILS: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    command_item.add_details,
                ),
                CommandHandler("skip", command_item.skip_details),
            ],
            LOOP: [
                CommandHandler("another", command_item.another_item),
            ],
        },
        fallbacks=[CommandHandler("cancel", command_item.cancel)],
        allow_reentry=True,
        run_async=False,
        persistent=True,
    )
    dp.add_handler(add_item_conversation)
    dp.add_handler(CommandHandler("done", command_item.done_item))

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    return dp


def run_pooling():
    """Run bot in pooling mode"""
    bot_persistence = PicklePersistence(filename="bot_persistence.pickle")
    updater = Updater(
        TELEGRAM_TOKEN,
        use_context=True,
        persistence=bot_persistence,
    )
    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = "https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")

    updater.start_polling()
    updater.idle()


# Global variable - best way I found to init Telegram bot
bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid {TELEGRAM_TOKEN}.")
    sys.exit(1)


def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    print(
        "update_json for debug:\n",
        update_json,
        "\n update for debug:\n",
        update,
    )
    dispatcher.process_update(update)


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands: Dict[str, Dict[str, str]] = {
        "en": {
            "start": "Start shopping bot 🛒",
            "add_item": "Add item to cart 👜",
            "add_info": "Add your info 📪",
            "followup": "Follow-up 🧾",
            "cancel": "cancel the bot 🔄",
            "delete_info": "Delete your info 🗑",
        },
        "fa": {
            "start": "بریم خرید 🛒",
            "add_item": "اضافه کردن به سبد خرید 👜",
            "add_info": "وارد کردن اطلاعات 📪",
            "followup": "آخرین سفارش خود را پیگیری کنید 🧾",
            "cancel": "خاموش کردن بات 🔄",
            "delete_info": "پاک کردن اطلاعات 🗑",
        },
    }

    bot_instance.delete_my_commands()
    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description)
                for command, description in langs_with_commands[
                    language_code
                ].items()
            ],
        )


# WARNING: it's better to comment the line below in DEBUG mode.
# Likely, you'll get a flood limit control error, when restarting bot too often
set_up_commands(bot)
n_workers = 0 if DEBUG else 4


bot_persistence = PicklePersistence(filename="bot_persistence.pickle")
dispatcher = Dispatcher(
    bot,
    update_queue=None,
    workers=n_workers,
    use_context=True,
    persistence=bot_persistence,
)

setup_dispatcher(dispatcher)
