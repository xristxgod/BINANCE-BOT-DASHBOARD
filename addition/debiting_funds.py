import asyncio
import typing
import decimal

from addition.config import logger, percentage_of_pnl
from addition.db_wallet import (
    get_users, get_profit_today_by_api_label, inset_new_balance_by_api_label,
    get_api_label_list_by_user_id, get_user_balance_by_api_label
)

async def get_realised_pnl_for_today(api_label: str) -> typing.Union[decimal.Decimal, int]:
    profit: decimal.Decimal = get_profit_today_by_api_label(api_label=api_label)
    if profit >= 0:
        return profit
    return 0

def withdraw_from_account(user: typing.Dict, api_label: str, profit_today: decimal.Decimal) -> bool:
    balance: decimal.Decimal = get_user_balance_by_api_label(api_label=api_label)
    balance -= profit_today
    logger.error(
        (
            f"The commission was withdrawn in the amount of: {profit_today} "
            f"| ID: {user['id']} "
            f"| Username: {user['username']} "
            f"| API LABEL: {api_label}"
        )
    )
    inset_new_balance_by_api_label(new_balance="%.8f" % balance, user_id=user["id"], api_label=api_label)
    logger.error(
        (
            f"The new balance has been recorded: {balance} "
            f"| ID: {user['id']} "
            f"| Username: {user['username']} "
            f"| API LABEL: {api_label}"
        )
    )
    return True

async def check_user(user: typing.Dict) -> bool:
    api_labels_list: typing.List = get_api_label_list_by_user_id(user_id=user["id"])
    for api_label in api_labels_list:
        logger.error(
            f"Starting balance collection | ID: {user['id']} | Username: {user['username']} | API LABEL: {api_label}"
        )
        profit_today = await get_realised_pnl_for_today(api_label=api_label)
        logger.error(
            f"Profit today: {profit_today} | ID: {user['id']} | Username: {user['username']} | API LABEL: {api_label}"
        )
        if profit_today == 0:
            continue
        percent_profit_today = profit_today / 100 * percentage_of_pnl
        withdraw_from_account(user=user, api_label=api_label, profit_today=percent_profit_today)
    logger.error(
        f"End of user verification | ID: {user['id']} | Username: {user['username']}"
    )
    return True

async def run():
    users = get_users()
    await asyncio.gather(*[
        check_user(user)
        for user in users
    ])

def main():
    asyncio.run(run())

if __name__ == '__main__':
    main()