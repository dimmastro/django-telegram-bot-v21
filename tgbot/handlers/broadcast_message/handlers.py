import re

import telegram
from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CallbackContext

from dtb.settings import DEBUG
from .manage_data import CONFIRM_DECLINE_BROADCAST, CONFIRM_BROADCAST
from .keyboards import keyboard_confirm_decline_broadcasting
from .static_text import broadcast_command, broadcast_wrong_format, broadcast_no_access, error_with_html, \
    message_is_sent, declined_message_broadcasting
from users.models import User
from users.tasks import broadcast_message
from telegram.constants import ParseMode

async def broadcast_command_with_message(update: Update, context: CallbackContext):
    """ Type /broadcast <some_text>. Then check your message in HTML format and broadcast to users."""
    u = await User.get_user(update, context)

    if not u.is_admin:
        await update.message.reply_text(
            text=broadcast_no_access,
        )
    else:
        if update.message.text == broadcast_command:
            # user typed only command without text for the message.
            await update.message.reply_text(
                text=broadcast_wrong_format,
                parse_mode=ParseMode.HTML,
            )
            return

        text = f"{update.message.text.replace(f'{broadcast_command} ', '')}"
        markup = keyboard_confirm_decline_broadcasting()

        try:
            await update.message.reply_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=markup,
            )
        except telegram.error.BadRequest as e:
            await update.message.reply_text(
                text=error_with_html.format(reason=e),
                parse_mode=ParseMode.HTML,
            )

from django.db.models import QuerySet
async def broadcast_decision_handler(update: Update, context: CallbackContext) -> None:
    # callback_data: CONFIRM_DECLINE_BROADCAST variable from manage_data.py
    """ Entered /broadcast <some_text>.
        Shows text in HTML style with two buttons:
        Confirm and Decline
    """
    broadcast_decision = update.callback_query.data[len(CONFIRM_DECLINE_BROADCAST):]

    entities_for_celery_to_dict = update.callback_query.message.to_dict()
    entities_for_celery = entities_for_celery_to_dict.get('entities')
    entities, text = update.callback_query.message.entities, update.callback_query.message.text

    if broadcast_decision == CONFIRM_BROADCAST:
        admin_text = message_is_sent
        users_all = await sync_to_async(User.objects.all)()
        users_filter = await sync_to_async(users_all.values_list)('user_id', flat=True)
        # users_all: QuerySet = await sync_to_async(User.objects.all)()
        # users_filter: QuerySet = await sync_to_async(users_all.values_list)('user_id', flat=True)

        user_ids = await sync_to_async(list)(users_filter)

        if DEBUG:
            await broadcast_message(
                user_ids=user_ids,
                text=text,
                entities=entities_for_celery,
            )
        else:
            # send in async mode via celery
            await broadcast_message.delay(
                user_ids=user_ids,
                text=text,
                entities=entities_for_celery,
            )
    else:
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=declined_message_broadcasting,
        )
        admin_text = text

    await context.bot.edit_message_text(
        text=admin_text,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        entities=None if broadcast_decision == CONFIRM_BROADCAST else entities,
    )
