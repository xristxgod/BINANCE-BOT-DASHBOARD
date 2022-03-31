import decimal

from addition.db_wallet import get_user_info_by_id, get_user_tg_id_by_user_id
from addition.config import symbol, ADMIN_IDS, ADMIN_TOKEN, USER_TOKEN

import requests

def send_to_admin_bot(user_id: int, amount: decimal.Decimal):
    user_info = get_user_info_by_id(user_id=user_id)
    text = (
        f"{symbol['add']} <b>There was a replenishment: {'%.8f' % amount} USDT</b>\n"
        f"<b>Username</b>: {user_info['username']}\n"
        f"<b>Email</b>: {user_info['email']}\n"
    )
    try:
        for admin_id in ADMIN_IDS:
            requests.get(f"https://api.telegram.org/bot{ADMIN_TOKEN}/sendMessage", params={
                "chat_id": admin_id,
                "text": text,
                "parse_mode": "html"
            })
        return True
    except Exception as error:
        raise error

def send_to_user_bot(user_id: int, amount: decimal.Decimal, is_add: bool = True):
    user_info = get_user_info_by_id(user_id=user_id)
    user_chat_id: int = get_user_tg_id_by_user_id(user_id=user_id)
    if user_chat_id is None:
        return True
    if is_add:
        text = (
            f"{symbol['add']} <b>There was a replenishment: {'%.8f' % amount} USDT</b>\n"
        )
    else:
        text = (
            f"{symbol['dec']} <b>There was a debited: {'%.8f' % amount} USDT</b>\n"
        )

    text += (
        f"<b>Username</b>: {user_info['username']}\n"
        f"<b>Email</b>: {user_info['email']}\n"
    )
    try:
        requests.get(f"https://api.telegram.org/bot{USER_TOKEN}/sendMessage", params={
            "chat_id": user_chat_id,
            "text": text,
            "parse_mode": "html"
        })
        return True
    except Exception as error:
        raise error