import asyncio

from addition.tron_net import tron_node
from addition.config import adminWallet, decimals

async def get_trx_for_fee(to_address, fee) -> bool:
    try:
        txn = tron_node.create_sign_transaction(
            from_address=adminWallet["address"],
            to_address=to_address,
            amount=fee,
            from_private_key=adminWallet["privateKey"]
        )
        return txn is not None
    except Exception as error:
        return False

async def send_to_main_wallet_token(address: str, private_key: str, amount: int) -> str:
    try:
        fee = tron_node.get_optimal_fee(from_address=address, to_address=adminWallet["address"])
    except Exception as error:
        if str(error) == "account not found on-chain":
            await get_trx_for_fee(to_address=address, fee=decimals.create_decimal("0.000001"))
            await asyncio.sleep(2)
            fee = tron_node.get_optimal_fee(from_address=address, to_address=adminWallet["address"])
        else:
            raise error
    balance_trx = tron_node.get_balance(address=address)
    if balance_trx - fee <= 0:
        fee_status = await get_trx_for_fee(to_address=address, fee=fee)
        now_balance_trx = tron_node.get_balance(address=address)
        if not fee_status or now_balance_trx - fee >= 0:
            return None
        await asyncio.sleep(10)
    txn = tron_node.create_sign_trc20_transactions(
        from_address=address, to_address=adminWallet["address"], amount=amount,
        from_private_key=private_key
    )
    if txn is not None:
        return txn
    return None