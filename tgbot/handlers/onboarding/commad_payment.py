import time
from io import BytesIO

import telegram
from dtb.settings import POLL, RECEIPT
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from tgbot.models import Order, User


def check(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    user_last_order = Order.objects.filter(user=u)[0]
    if user_last_order.is_paid is False:
        update.message.reply_markdown(
            text="Send the screeshot of you'r peyment receipt for the order:\n{order}".format(
                order=user_last_order
            )
        )
    else:
        update.message.reply_markdown(
            text="Your last order\n{order}\n is paid.".format(
                order=user_last_order
            )
        )
        return ConversationHandler.END
    return RECEIPT


def photo_handler(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    admin = User.objects.filter(is_admin=True)
    order = Order.objects.filter(user=u)[0]  # .order_by("-id").first()

    file = context.bot.get_file(update.message.photo[-1].file_id)
    f = BytesIO(file.download_as_bytearray())

    time.sleep(2)
    update.message.reply_text(
        text="We will proccess the reciept and get back to you soon."
    )
    if u not in admin:
        return ConversationHandler.END

    reply_markup = telegram.ReplyKeyboardMarkup(
        [
            [
                telegram.KeyboardButton(
                    "Verify\n{order_id}".format(order_id=order.id)
                )
            ],
            [
                telegram.KeyboardButton(
                    "Reject\n{order_id}".format(order_id=order.id)
                )
            ],
        ],
        resize_keyboard=True,
        request_poll=True,
        # one_time_keyboard=True,
    )
    context.bot.sendPhoto(
        chat_id=admin[0].user_id,
        photo=f,
        caption="Tracking number for this order is:\n{no}".format(no=order.id),
        reply_markup=reply_markup,
    )
    return POLL


def poll(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    admin = User.objects.filter(is_admin=True)
    markup = telegram.ReplyKeyboardRemove()
    if u not in admin:
        return ConversationHandler.END
    else:
        answer = update.message.text
        if "Verify\n" in answer:
            order_id = answer.replace("Verify\n", "")
            order = Order.objects.get(id=order_id)
            order.is_paid = True
            order.save()
            time.sleep(2)
            update.message.reply_text(
                text="Your answer was {poll} to pyment ".format(
                    poll=update.message.text
                ),
                reply_markup=markup,
            )
            context.bot.send_message(
                chat_id=order.user.user_id,
                text="Your peyment for order no.{order_id} is verified.".format(
                    order_id=order_id
                ),
            )

        elif "Reject\n" in answer:
            order_id = answer.replace("Reject\n", "")
            time.sleep(2)
            update.message.reply_text(
                text="Your answer was {poll} to pyment ".format(
                    poll=update.message.text
                ),
                reply_markup=markup,
            )
            context.bot.send_message(
                chat_id=order.user.user_id,
                text="Your peyment for order no.{order_id} is NOT verified.".format(
                    order_id=order_id
                ),
            )
    return ConversationHandler.END
