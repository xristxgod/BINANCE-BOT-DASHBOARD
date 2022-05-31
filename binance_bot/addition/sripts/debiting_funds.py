import asyncio

from futuresboard.blueprint import DB
from addition.tg_bot.send_to_bot import send_to_user_bot
from addition.config import logger, percentage_of_pnl, decimals

def withdraw_from_account(user, profit_today: float, new_balance: float) -> bool:
    status_insert_withdraw: bool = DB.insert_new_withdraw(user=user, profit_today=profit_today)
    if not status_insert_withdraw:
        return False
    send_to_user_bot(user_id=user.id, amount=decimals.create_decimal(profit_today), is_add=False)
    return DB.insert_new_balance(user=user, new_balance=new_balance)

async def check_user(user) -> bool:
    api_labels_list = DB.get_api_labels_list(user_id=user.id)
    if len(api_labels_list) == 0:
        return True
    profit_today: float = 0.0
    for api_label in api_labels_list:
        realised_pnl = DB.get_realised_pnl_for_today(api_label=api_label, user_id=user.id)
        profit_today += realised_pnl
    if profit_today <= 0:
        return True
    our_percent = profit_today / 100 * percentage_of_pnl
    logger.error((
        f"PROFIT PER DAY: {profit_today} | OUR PERCENT: {our_percent} | "
        f"USERNAME: {user.username} | BALANCE: {user.budget}"
    ))
    return withdraw_from_account(user=user, profit_today=our_percent, new_balance=float(user.budget) - our_percent)

async def run():
    users = DB.get_users()
    logger.error("\nSTART DEBITING FUNDS!")
    await asyncio.gather(*[
        check_user(user)
        for user in users
    ])
    logger.error("END DEBITING FUNDS\n")

def main():
    asyncio.run(run())

if __name__ == '__main__':
    main()
