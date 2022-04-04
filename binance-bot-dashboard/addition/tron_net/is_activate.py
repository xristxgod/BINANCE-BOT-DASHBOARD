import typing
import asyncio
from datetime import datetime

from addition.tg_bot.send_to_bot import send_to_admin_bot, send_to_user_bot
from addition.tron_net.tron_wallet import (
    get_wallet_by_user_id, get_wallet_info_by_user_id,
    insert_transaction, update_status_sub, update_balance
)
from addition.tron_net import tron_node
from addition.tron_net.tron_balancer import send_to_main_wallet_token
from addition.config import LIMIT_USDT, decimals

def is_activate(user_id: int) -> bool:
    wallet = get_wallet_by_user_id(user_id=user_id)
    balance = tron_node.get_token_balance(address=wallet["address"])
    if balance > LIMIT_USDT:
        return transfer_to_the_central_wallet(user_id=user_id, amount=balance)

def create_and_sign_transaction(address: str, private_key: str, amount) -> typing.Dict:

    result = asyncio.run(send_to_main_wallet_token(address=address, private_key=private_key, amount=amount))
    if result is None:
        return None
    return {
        "timestamp": int(datetime.timestamp(datetime.now())) * 1000,
        "tx_id": result
    }

def transfer_to_the_central_wallet(user_id: int, amount):
    wallet_info = get_wallet_info_by_user_id(user_id=user_id)
    tx_info = create_and_sign_transaction(address=wallet_info["address"], private_key=wallet_info["private_key"], amount=amount)
    if tx_info is None:
        return False
    status = insert_transaction(
        timestamp=tx_info["timestamp"],
        tx_id=tx_info["tx_id"],
        user_id=user_id,
        amount=amount
    )
    if status:
        update_balance(user_id=user_id, balance=amount)
        send_to_admin_bot(user_id=user_id, amount=decimals.create_decimal(amount))
        send_to_user_bot(user_id=user_id, amount=decimals.create_decimal(amount), is_add=True)
        return update_status_sub(status=True, last_time=tx_info["timestamp"], user_id=user_id)
    return False