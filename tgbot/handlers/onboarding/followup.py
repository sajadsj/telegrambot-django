import datetime
import time

from django.utils import timezone
from dtb.settings import (
    ADDRESS,
    COLOR,
    COUNT,
    DEL,
    DELETE_INFO,
    DETAILS,
    INFO,
    LOOP,
    PAY,
    PHONE,
    PRICE,
    SALES_LINK,
    SIZE,
)
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler
from tgbot.handlers.onboarding import static_text
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.models import Item, Order, RutinUpdate, User


def get_order_by_id(id=id):
    return Order.objects.get(id=id)


def delete_order_by_id(id=id):
    record = Order.objects.get(id=id)
    record.delete()


def my_order(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    if not Order.objects.filter(user=u):
        update.message.reply_text(
            text="You did not ordered yet.Order using this command: /add_item"
        )
    else:
        last_order = Order.objects.filter(user=u)[0]
        if last_order.is_paid is False:
            update.message.reply_text(text=str(last_order))
            update.message.reply_text(
                text="Pay using this command: /peyment_check"
            )

        else:
            update.message.reply_text(text=last_order)
