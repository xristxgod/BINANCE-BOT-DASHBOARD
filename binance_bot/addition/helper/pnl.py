import typing

from addition.db_wallet import get_user_budget_by_api_label, get_users_sum_budget_by_ids
from addition.config import decimals

def get_percent_unrealised_pnl(unrealised_pnl: int, api_label: str):
    if unrealised_pnl == 0:
        return "-"
    else:
        balance = get_user_budget_by_api_label(api_label=api_label)
        return "%.2f" % (100 / (balance / decimals.create_decimal(unrealised_pnl)))

def get_percent_unrealised_pnl_for_all(unrealised_pnl: int, users_ids: typing.Tuple[int]):
    if unrealised_pnl == 0:
        return "-"
    else:
        balance = get_users_sum_budget_by_ids(users_ids=users_ids)
        return "%.2f" % (100 / (balance / decimals.create_decimal(unrealised_pnl)))