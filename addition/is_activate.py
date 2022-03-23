import typing
import uuid
from datetime import datetime, timedelta
from tronpy.tron import Tron, HTTPProvider

from addition.utils import get_token, is_confirm
from addition.tron_wallet import (
    get_wallet_by_user_id, get_wallet_info_by_user_id,
    insert_transaction, update_status_sub
)
from addition.config import _network, _node_url

def get_wallet_balance(address):
    node = Tron(
        provider=HTTPProvider(_node_url) if _network == "mainnet" else None,
        network=_network
    )
    # We get information about the token
    token = get_token(network=_network)
    # Connecting to the token (smart contract)
    contract = node.get_contract(token["contract_address"])
    if is_confirm(contract.functions.balanceOf(address), token):
        return True
    return False

def is_activate(user_id: int) -> bool:
    wallet = get_wallet_by_user_id(user_id=user_id)
    if bool(wallet["status"]):
        if "last_activate_time" in wallet and \
                datetime.fromtimestamp(int(wallet["last_activate_time"]) / 1000).date() + timedelta(days=7) >= datetime.now().date():
            return True
        else:
            update_status_sub(user_id=user_id, status=False)
            return is_activate(user_id=user_id)
    else:
        if not get_wallet_balance(wallet["address"]):
            return False
        else:
            return transfer_to_the_central_wallet(user_id=user_id)

def create_and_sign_transaction(address: str, private_key: str) -> typing.Dict:
    return {
        "timestamp": int(datetime.timestamp(datetime.now())) * 1000,
        "tx_id": str(uuid.uuid4().hex)
    }

def transfer_to_the_central_wallet(user_id: int):
    wallet_info = get_wallet_info_by_user_id(user_id=user_id)
    tx_info = create_and_sign_transaction(address=wallet_info["address"], private_key=wallet_info["private_key"])
    status = insert_transaction(
        timestamp=tx_info["timestamp"],
        tx_id=tx_info["tx_id"],
        user_id=user_id,
        amount=100
    )
    if status:
        return update_status_sub(status=True, last_time=tx_info["timestamp"], user_id=user_id)
    return False