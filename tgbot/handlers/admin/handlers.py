from datetime import timedelta

from asgiref.sync import sync_to_async
from django.utils.timezone import now
from telegram import Update
from telegram.ext import CallbackContext

from tgbot.handlers.admin import static_text
from tgbot.handlers.admin.utils import _get_csv_from_qs_values
from tgbot.handlers.utils.decorators import admin_only, send_typing_action
from users.models import User

from telegram.constants import ParseMode

@admin_only
async def admin(update: Update, context: CallbackContext) -> None:
    """ Show help info about all secret admins commands """
    await update.message.reply_text(static_text.secret_admin_commands)


@admin_only
async def stats(update: Update, context: CallbackContext) -> None:
    """ Show help info about all secret admins commands """
    user_count = await sync_to_async(User.objects.count)()
    active_24_u = await sync_to_async(User.objects.filter)(updated_at__gte=now() - timedelta(hours=24))
    active_24 = await sync_to_async(active_24_u.count)()
    text = static_text.users_amount_stat.format(
        user_count=user_count,
        active_24=active_24
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


# @send_typing_action
@admin_only
async def export_users(update: Update, context: CallbackContext) -> None:
    # in values argument you can specify which fields should be returned in output csv
    users_all = await sync_to_async(User.objects.all)()
    users = await sync_to_async(users_all.values)()
    csv_users = await _get_csv_from_qs_values(users)
    await update.message.reply_document(csv_users)
