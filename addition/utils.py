import typing
import decimal
from datetime import date
from datetime import timedelta

from addition.config import decimals

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_token(network: str) -> typing.Dict:
    """Return information about the token."""
    if network == "mainnet":
        return {
            "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
            "decimal": 6
        }
    elif network == "shasta":
        return {
            "contract_address": "TRvz1r3URQq5otL7ioTbxVUfim9RVSm1hA",
            "decimal": 6
        }
    else:
        return {}

def get_fee(balance: decimal.Decimal) -> decimal.Decimal:
    if balance > 0:
        return decimals.create_decimal(4.2)
    else:
        return decimals.create_decimal(8.9)

def is_balance(result: int, token_decimal: int, amount_right: decimal.Decimal = decimals.create_decimal("100")) -> bool:
    """
    If the balance is not empty, then we will find out the amount of funds in the wallet.
    :param amount_right: The required number of coins in the account.
    :return:
    """
    balance = result / (10 ** token_decimal)
    return decimals.create_decimal(balance) >= amount_right

def is_confirm(result: int, token: typing.Dict):
    """
    We transfer the token balance and check it.
    :param result: Balance in integer.
    :param token: Information about the token.
    """

    if int(result) > 0:
        # If the balance is not empty, then we will find out the amount of funds in the wallet.
        if is_balance(result=result, token_decimal=token["decimal"]):
            return True
        else:
            return False
    else:
        return False

def timeranges():
    today = date.today()
    yesterday_start = today - timedelta(days=1)

    this_week_start = today - timedelta(days=today.weekday())
    last_week_start = this_week_start - timedelta(days=7)
    last_week_end = this_week_start - timedelta(days=1)

    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)

    this_year_start = today.replace(day=1).replace(month=1)
    last_year_start = (this_year_start - timedelta(days=1)).replace(day=1).replace(month=1)
    last_year_end = this_year_start - timedelta(days=1)

    return [
        [today.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")],
        [yesterday_start.strftime("%Y-%m-%d"), yesterday_start.strftime("%Y-%m-%d")],
        [this_week_start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")],
        [last_week_start.strftime("%Y-%m-%d"), last_week_end.strftime("%Y-%m-%d")],
        [this_month_start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")],
        [last_month_start.strftime("%Y-%m-%d"), last_month_end.strftime("%Y-%m-%d")],
        [this_year_start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")],
        [last_year_start.strftime("%Y-%m-%d"), last_year_end.strftime("%Y-%m-%d")],
        [last_year_start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")],
    ]