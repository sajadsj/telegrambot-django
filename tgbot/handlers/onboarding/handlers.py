from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from tgbot.handlers.onboarding import static_text
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command
from tgbot.models import User


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    if created:
        if u.address is None or u.phone is None:
            text = static_text.start_created.format(first_name=u.first_name)
            update.message.reply_text(text=text)
            return
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)
        update.message.reply_text(
            text=text, reply_markup=make_keyboard_for_start_command()
        )
        return


def cancel_info(update: Update, context: CallbackContext) -> None:
    return ConversationHandler.END
