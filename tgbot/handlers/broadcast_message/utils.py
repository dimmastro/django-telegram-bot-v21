from typing import Union, Optional, Dict, List

import telegram
from asgiref.sync import sync_to_async
from telegram import MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup

from dtb.settings import TELEGRAM_TOKEN
from users.models import User

from telegram.constants import ParseMode

async def from_celery_markup_to_markup(celery_markup: Optional[List[List[Dict]]]) -> Optional[InlineKeyboardMarkup]:
    markup = None
    if celery_markup:
        markup = []
        for row_of_buttons in celery_markup:
            row = []
            for button in row_of_buttons:
                row.append(
                    InlineKeyboardButton(
                        text=button['text'],
                        callback_data=button.get('callback_data'),
                        url=button.get('url'),
                    )
                )
            markup.append(row)
        markup = InlineKeyboardMarkup(markup)
    return markup


async def from_celery_entities_to_entities(celery_entities: Optional[List[Dict]] = None) -> Optional[List[MessageEntity]]:
    entities = None
    if celery_entities:
        entities = [
            MessageEntity(
                type=entity['type'],
                offset=entity['offset'],
                length=entity['length'],
                url=entity.get('url'),
                language=entity.get('language'),
            )
            for entity in celery_entities
        ]
    return entities


async def send_one_message(
    user_id: Union[str, int],
    text: str,
    parse_mode: Optional[str] = ParseMode.HTML,
    reply_markup: Optional[List[List[Dict]]] = None,
    reply_to_message_id: Optional[int] = None,
    disable_web_page_preview: Optional[bool] = None,
    entities: Optional[List[MessageEntity]] = None,
    tg_token: str = TELEGRAM_TOKEN,
) -> bool:
    bot = telegram.Bot(tg_token)
    try:
        m = await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
        )
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        await User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    else:
        success = True
        # await User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
        user_filter = await sync_to_async(User.objects.filter)(user_id=user_id)
        await sync_to_async(user_filter.update)(is_blocked_bot=False)
    return success
