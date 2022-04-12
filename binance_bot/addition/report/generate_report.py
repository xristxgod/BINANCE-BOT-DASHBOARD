import typing
import sqlite3
from datetime import datetime
import json

from addition.utils import dict_factory
from addition.config import db_path, decimals
from addition.db_wallet import get_users, get_api_label_list_by_user_id

def get_referral_profit(user_id: int, start: int, end: int):
    sql = (
        f"SELECT time, lvl "
        f"FROM referral_profit_model "
        f"WHERE user_id={user_id} "
        f"AND time >= {start // 1000} "
        f"AND time <= {end // 1000};"
    )
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        result = cursor.execute(sql).fetchall()
        if result is not None or result != []:
            ref = []
            for i in result:
                i["lvl"] = json.loads(i["lvl"])
                i["time"] = str(datetime.fromtimestamp(i["time"]))
                ref.append(i)
            return ref
        return {}
    except Exception as error:
        return {}
    finally:
        if connection is not None:
            connection.close()

def get_user_balance(user_id: int):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        return "%.8f" % decimals.create_decimal(cursor.execute(
            f"SELECT budget FROM user_model WHERE id={user_id}"
        ).fetchone()[0])
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_profit_bot(start: int, end: int, user_id: int):
    connection = None
    result = []
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        api_labels_list: typing.List = get_api_label_list_by_user_id(user_id=user_id)
        for api_label in api_labels_list:
            income = cursor.execute(
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
            result.append({
                "name": api_label,
                "income": "%.8f" % decimals.create_decimal(income) if income is not None else 0
            })
        return result
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_withdraw_history(start: int, end: int, user_id: int) -> typing.List[typing.Dict]:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        result = cursor.execute(
            (
                'SELECT time, amount FROM withdraw_model '
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

def get_deposit_history(start: int, end: int, user_id: int) -> typing.List[typing.Dict]:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        result = cursor.execute(
            (
                'SELECT time, amount FROM tron_transaction_model '
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

def get_report(start: int, end: int, user_id: int):
    return {
        # сколько заработал бот за период
        "profit_period": get_profit_bot(start=start, end=end, user_id=user_id),
        # сколько списал и когда
        "withdraw_history": get_withdraw_history(start=start, end=end, user_id=user_id),
        # сколько пользователь пополнил и когда
        "deposit_history": get_deposit_history(start=start, end=end, user_id=user_id),
        # отображать остаток
        "balance": get_user_balance(user_id=user_id),
        # Профит по рефералу
        "referral_profit": get_referral_profit(start=start, end=end, user_id=user_id)
    }

def get_report_by_all_users(start: int, end: int):
    users = get_users()
    all_report = []
    for user in users:
        all_report.append(
            {
                "username": user["username"],
                "report": get_report(start=start, end=end, user_id=user["id"])
            }
        )
    return all_report