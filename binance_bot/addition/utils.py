import secrets
import string
import base64
from decimal import Decimal, localcontext
import typing
import decimal
from datetime import date
from datetime import timedelta

from addition.config import decimals

TIMERS = 10
SUN = Decimal("1000000")
MIN_SUN = 0
MAX_SUN = 2**256 - 1

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

def is_balance(balance) -> bool:
    """
    If the balance is not empty, then we will find out the amount of funds in the wallet.
    :param amount_right: The required number of coins in the account.
    :return:
    """
    return decimals.create_decimal(balance) >= 2

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

def generate_referral_code():
    return "".join(secrets.choice(string.ascii_letters + string.digits) for i in range(5))

def from_sun(num):
    """
    Helper function that will convert a value in TRX to SUN
    :param num: Value in TRX to convert to SUN
    """
    if num == 0:
        return 0
    if num < MIN_SUN or num > MAX_SUN:
        raise ValueError("Value must be between 1 and 2**256 - 1")

    unit_value = SUN

    with localcontext() as ctx:
        ctx.prec = 999
        d_num = Decimal(value=num, context=ctx)
        result = d_num / unit_value

    return result

def to_sun(num) -> int:
    """
    Helper function that will convert a value in TRX to SUN
    :param num: Value in TRX to convert to SUN
    """
    if isinstance(num, int) or isinstance(num, str):
        d_num = Decimal(value=num)
    elif isinstance(num, float):
        d_num = Decimal(value=str(num))
    elif isinstance(num, Decimal):
        d_num = num
    else:
        raise TypeError("Unsupported type. Must be one of integer, float, or string")

    s_num = str(num)
    unit_value = SUN

    if d_num == 0:
        return 0

    if d_num < 1 and "." in s_num:
        with localcontext() as ctx:
            multiplier = len(s_num) - s_num.index(".") - 1
            ctx.prec = multiplier
            d_num = Decimal(value=num, context=ctx) * 10 ** multiplier
        unit_value /= 10 ** multiplier

    with localcontext() as ctx:
        ctx.prec = 999
        result = Decimal(value=d_num, context=ctx) * unit_value

    if result < MIN_SUN or result > MAX_SUN:
        raise ValueError("Resulting wei value must be between 1 and 2**256 - 1")

    return int(result)

def generate_token_code():
    return "".join(secrets.choice(string.ascii_letters + string.digits) for i in range(25))

def generate_code_for_google_authenticator():
    secret = "".join(secrets.choice(string.ascii_letters + string.digits) for i in range(16))
    return base64.b32encode(bytearray(secret, 'ascii')).decode('utf-8')[0:16]