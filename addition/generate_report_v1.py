import typing
import random
import sqlite3
import decimal
from datetime import datetime

from addition.utils import dict_factory
from addition.config import db_path, decimals

def get_user_balance_by_api_label(api_label: str) -> decimal.Decimal:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        return decimals.create_decimal(cursor.execute(
            f"SELECT totalWalletBalance FROM account_model WHERE api_label='{api_label}'"
        ).fetchone()[0])
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_bot_earned_for_the_period(start: int, end: int, api_label: str) -> decimal.Decimal:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        return cursor.execute(
            (
                'SELECT SUM(income) FROM income_model '
                'WHERE asset <> "BNB" '
                'AND incomeType <> "TRANSFER" '
                'AND time >= {} '
                'AND time <= {} '
                'AND api_label = "{}"'
            ).format(
                start, end, api_label
            )
        ).fetchone()[0]
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_withdraw_history(start: int, end: int, api_label: str) -> typing.List[typing.Dict]:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        result = cursor.execute(
            (
                'SELECT income, time FROM income_model '
                'WHERE asset <> "BNB" '
                'AND incomeType <> "COMMISSION" '
                'AND time >= {} '
                'AND time <= {} '
                'AND api_label = "{}"'
            ).format(
                start, end, api_label
            )
        ).fetchall()
        if len(result) <= 0:
            return []
        dict_withdraw = []
        for i in result:
            dict_withdraw.append({
                "time": datetime.fromtimestamp(int(i["time"]) / 1000),
                "amount": i["income"]
            })
        return dict_withdraw
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_deposit_history(start: int, end: int, user_id: int) -> typing.List[typing.Dict]:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        result = cursor.execute(
            (
                'SELECT time, tx_id, amount FROM tron_transaction_model '
                'WHERE time >= {} '
                'AND time <= {} '
                'AND user_id = {}'
            ).format(
                start, end, user_id
            )
        ).fetchall()
        if len(result) <= 0:
            return []
        dict_deposit = []
        for i in result:
            i["time"] = datetime.fromtimestamp(int(i["time"]) / 1000)
            dict_deposit.append(i)
        return dict_deposit
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_report(start: int, end: int, api_label: str, user_id: int):
    return {
        # сколько заработал бот за период
        "HowMuchDidTheBotEarnDuringThePeriod": get_bot_earned_for_the_period(start, end, api_label),
        # сколько списал и когда
        "HowMuchDidYouWithdrawAndWhen": get_withdraw_history(
            start=start, end=end, api_label=api_label
        ),
        # сколько пользователь пополнил и когда
        "HowMuchDidTheUserTopUpAndWhen": get_deposit_history(
            start=start, end=end, user_id=user_id
        ),
        # отображать остаток
        "Remains": get_user_balance_by_api_label(api_label=api_label)
    }