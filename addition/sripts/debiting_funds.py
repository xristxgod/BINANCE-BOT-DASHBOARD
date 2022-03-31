import asyncio
import typing
import decimal
from datetime import datetime

from addition.config import logger, percentage_of_pnl, decimals
from addition.tg_bot.send_to_bot import send_to_user_bot
from addition.db_wallet import (
    get_users, get_profit_today_by_api_label, inset_new_balance,
    get_api_label_list_by_user_id, get_user_balance, inset_withdraw
)

async def get_realised_pnl_for_today(api_label: str) -> typing.Union[decimal.Decimal, int]:
    profit: decimal.Decimal = get_profit_today_by_api_label(api_label=api_label)
    if profit >= 0:
        return profit
    return 0

def withdraw_from_account(user: typing.Dict, profit_today: decimal.Decimal) -> bool:
    balance: decimal.Decimal = get_user_balance(user_id=user["id"])
    balance -= profit_today
    inset_withdraw(ins_time=int(datetime.timestamp(datetime.now())) * 1000, amount="%.8f" % profit_today, user_id=user["id"])
    send_to_user_bot(user_id=user["id"], amount=profit_today, is_add=False)
    return inset_new_balance(new_balance="%.8f" % balance, user_id=user["id"])

async def check_user(user: typing.Dict) -> bool:
    api_labels_list: typing.List = get_api_label_list_by_user_id(user_id=user["id"])
    profit_today = 0
    for api_label in api_labels_list:
        realised_pnl = await get_realised_pnl_for_today(api_label=api_label)
        if realised_pnl <= 0:
            continue
        else:
            profit_today += realised_pnl
    if profit_today == 0:
        return True
    else:
        percent_profit_today = profit_today / 100 * percentage_of_pnl
        withdraw_from_account(user=user, profit_today=decimals.create_decimal(percent_profit_today))
        return True

async def run():
    users = get_users()
    logger.error("START debiting_funds.py")
    await asyncio.gather(*[
        check_user(user)
        for user in users
    ])
    logger.error("END debiting_funds.py")

def main():
    asyncio.run(run())

if __name__ == '__main__':
    main()