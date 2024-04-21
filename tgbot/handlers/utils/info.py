from typing import Dict

from telegram import Update


from typing import Dict
from telegram import Update

def extract_user_data_from_update(update: Update) -> Dict:
    """Extracts user data from a telegram Update."""
    user_data = {
        "user_id": None,
        "is_blocked_bot": False,
        "username": None,
        "first_name": None,
        "last_name": None,
        "language_code": None,
    }

    if update.effective_user:
        user = update.effective_user.to_dict()
        user_data.update(
            {
                "user_id": user.get("id"),
                "username": user.get("username"),
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "language_code": user.get("language_code"),
            }
        )

    return user_data
