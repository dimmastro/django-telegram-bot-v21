import datetime

from django.utils import timezone
from telegram import Update
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from users.models import User
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command

from telegram.constants import ParseMode
from asgiref.sync import sync_to_async
async def command_start(update: Update, context: CallbackContext) -> None:
    u, created = await User.get_user_and_created(update, context)

    if created:
        text = static_text.start_created.format(first_name=u.first_name)
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)

    await update.message.reply_text(text=text,
                              reply_markup=make_keyboard_for_start_command())


from asgiref.sync import sync_to_async


async def secret_level(update: Update, context: CallbackContext) -> None:
    # callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """ Pressed 'secret_level_button_text' after /start command"""
    user_id = extract_user_data_from_update(update)['user_id']
    user_count = await sync_to_async(User.objects.count)()
    active_24_u = await sync_to_async(User.objects.filter)(updated_at__gte=timezone.now() - datetime.timedelta(hours=24))
    active_24 = await sync_to_async(active_24_u.count)()

    text = static_text.unlock_secret_room.format(
        user_count=user_count,
        active_24=active_24
    )

    await context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML
    )
