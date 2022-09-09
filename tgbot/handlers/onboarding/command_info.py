import datetime
import time

import telegram
from django.utils import timezone
from dtb.settings import (
    ADDRESS,
    COUNT,
    DELETE_INFO,
    DETAILS,
    INFO,
    LOOP,
    PHONE,
    PRICE,
    SALES_LINK,
)
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler
from tgbot.handlers.onboarding import static_text
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.models import Item, Order, RutinUpdate, User


def command_add_info(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    if u.address is not None and u.phone is not None:
        text = static_text.add_info_already_exists.format(
            first_name=u.first_name
        )
        time.sleep(2)  # to prevent the bot from sending the message too fast
        update.message.reply_text(text=text)
        return ConversationHandler.END
    else:
        update.message.reply_text(
            text="Enter Your Address or your cargo address:"
        )
        return ADDRESS


def add_address(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    address = update.message.text
    u.address = address
    u.save()
    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(text="Address added.")
    # update.message.reply_text(text="Enter Your phone number:")

    reply_markup = telegram.ReplyKeyboardMarkup(
        [[telegram.KeyboardButton("Share contact", request_contact=True)]],
        resize_keyboard=True,
    )
    update.message.reply_text(
        text="Enter Your phone number:", reply_markup=reply_markup
    )
    return PHONE


def add_phone(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    phone = update.message.contact.phone_number
    u.phone = phone
    u.save()
    # send a message and remove the keyboard
    markup = telegram.ReplyKeyboardRemove()
    update.message.reply_text(text="Phone added.", reply_markup=markup)
    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(
        text="Your address is:{address}\nand Your phone is: {phone}\nIf you are not happy with them use /delete_info".format(
            address=u.address, phone=u.phone
        )
    )
    return ConversationHandler.END


def cancel_info(update: Update, context: CallbackContext) -> None:
    return ConversationHandler.END


def command_del_info(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    if u.address is not None or u.phone is not None:
        u.address = None
        u.phone = None
        u.save()
        text = static_text.info_deleted.format(first_name=u.first_name)
        time.sleep(2)  # to prevent the bot from sending the message too fast
        update.message.reply_text(text=text)
        return
    else:
        text = static_text.info_null
        time.sleep(2)  # to prevent the bot from sending the message too fast
        update.message.reply_text(text=text)
        return
