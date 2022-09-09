import datetime
import time

from django.utils import timezone
from dtb.settings import (
    ADDRESS,
    COLOR,
    COUNT,
    DELETE_INFO,
    DETAILS,
    INFO,
    LOOP,
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


def command_add_item(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)

    if u.address is None or u.phone is None:
        text = static_text.info_null
        time.sleep(2)  # to prevent the bot from sending the message too fast
        update.message.reply_text(text=text)
        return ConversationHandler.END
    else:
        Order.objects.create(user=u)
        time.sleep(2)  # to prevent the bot from sending the message too fast
        update.message.reply_text(text="Enter item sales link:")
        return SALES_LINK


def add_sales_link(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    order = Order.objects.filter(user=u)[0]
    item = Item.objects.create(order=order)
    item.sales_link = update.message.text
    item.save()
    if item.sales_link:
        update.message.reply_text(text="sales link added.")
    else:
        update.message.reply_text(text="sales link not added.")
        return ConversationHandler.END

    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(text="Enter item price in tl:")
    return PRICE


def add_price(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    """ retrive the latest order """
    order = Order.objects.filter(user=u)[0]
    item = Item.objects.filter(order=order).order_by("-id").first()
    item.price_per_unit_in_tl = update.message.text
    item.save()
    if item.price_per_unit_in_tl:
        update.message.reply_text(text="price added.")
    else:
        update.message.reply_text(text="price link not added.")
        return ConversationHandler.END
    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(text="How many of this do you want?")
    return COUNT


def add_count(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    order = Order.objects.filter(user=u)[0]
    item = Item.objects.filter(order=order).order_by("-id").first()
    item.count = update.message.text
    item.save()
    if item.count:
        update.message.reply_text(text="count added.")
    else:
        update.message.reply_text(text="count not added.")
        return ConversationHandler.END

    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(text="What size:")
    return SIZE


def add_size(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    order = Order.objects.filter(user=u)[0]
    item = Item.objects.filter(order=order).order_by("-id").first()
    item.size = update.message.text
    item.save()
    if item.size:
        update.message.reply_text(text="size added.")
    else:
        update.message.reply_text(text="size not added.")
        return ConversationHandler.END
    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(text="What color:")
    return COLOR


def add_color(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    order = Order.objects.filter(user=u)[0]
    item = Item.objects.filter(order=order).order_by("-id").first()
    item.color = update.message.text
    item.save()
    if item.color:
        update.message.reply_text(text="color added.")
    else:
        update.message.reply_text(text="color not added.")
        return ConversationHandler.END
    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(text="Any details:\n If not /skip")
    return DETAILS


def add_details(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    order = Order.objects.filter(user=u)[0]
    item = Item.objects.filter(order=order).order_by("-id").first()
    item.detales = update.message.text
    item.save()

    for item in Item.objects.filter(order=order):
        order.all_to_pay += item.price_per_unit_in_tl * item.count
    order.save()
    if item.detales:
        update.message.reply_text(text="details added.")
    else:
        update.message.reply_text(text="details not added.")
        return ConversationHandler.END
    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(
        text="Here is your order: {order} \n If you want to add another item, /another or if it's done, /done".format(
            order=order
        )
    )
    return LOOP


def skip_details(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    order = Order.objects.filter(user=u)[0]
    for item in Item.objects.filter(order=order):
        order.all_to_pay += item.price_per_unit_in_tl * item.count
    order.save()
    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(
        text="Here is your order: {order} \n If you want to add another item, /another or if it's done, /done".format(
            order=order
        )
    )
    return LOOP


def another_item(update: Update, context: CallbackContext) -> None:
    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(text="Enter item sales link:")
    return SALES_LINK


def done_item(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    order = Order.objects.filter(user=u)[0]
    time.sleep(2)  # to prevent the bot from sending the message too fast
    update.message.reply_text(
        text="Thank you for your order: {order}.\nYour Tracking code is: {id}.\nYou need to pay {all_to_pay}".format(
            order=order, id=order.id, all_to_pay=order.all_to_pay
        )
    )

    today_price_in_tl = RutinUpdate.objects[0].today_price_in_tl
    card_no = RutinUpdate.objects[0].card_no
    update.message.reply_text(
        text="Your total price is: {total_price} toman.\nPlease charge it to {card_no}\nThen send the receipt using the commad //peyment_check".format(
            total_price=today_price_in_tl * order.all_to_pay, card_no=card_no
        )
    )

    return


def cancel(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text="Bot is off. Please, /start again.")
    return ConversationHandler.END
