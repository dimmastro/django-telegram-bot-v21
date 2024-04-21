from functools import wraps
from typing import Callable

from telegram import Update
from telegram.ext import CallbackContext

from users.models import User

from telegram.constants import ChatAction

def admin_only(func: Callable):
    """
    Admin only decorator
    Used for handlers that only admins have access to
    """

    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = await User.get_user(update, context)

        if not user.is_admin:
            return

        # Check if func is a coroutine function
        # if hasattr(func, '__await__'):
        #     return await func(update, context, *args, **kwargs)
        # else:
        #     return func(update, context, *args, **kwargs)
        return await func(update, context, *args, **kwargs)

    return wrapper


def send_typing_action(func: Callable):
    """Sends typing action while processing func command."""

    @wraps(func)
    async def command_func(update: Update, context: CallbackContext, *args, **kwargs):
        await update.effective_chat.send_chat_action(ChatAction.TYPING)

        if hasattr(func, '__await__'):
            return await func(update, context, *args, **kwargs)
        else:
            return func(update, context, *args, **kwargs)

    return command_func
