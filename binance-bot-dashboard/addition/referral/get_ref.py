import json
import sqlite3
import typing
import decimal
from datetime import datetime

from addition.db_wallet import get_user_balance
from addition.utils import dict_factory
from addition.config import db_path, decimals

def get_sql_from_db(sql: str) -> typing.Dict:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        result = cursor.execute(sql).fetchone()
        return result
    except Exception as error:
        return {}
    finally:
        if connection is not None:
            connection.close()

def get_lvl_1(users: typing.List[typing.Dict], balance: decimal.Decimal) -> typing.List[typing.Dict]:
    lvl_1_users: typing.List[typing.Dict] = []
    time_now = int(datetime.timestamp(datetime.now()))
    for user in users:
        sql = (
            f"SELECT SUM(income) AS income FROM income_model "
            f"WHERE user_id={user['user_id']} "
            f"AND time >= {user['time']} AND time <= {time_now} "
            f"AND asset <> 'BNB' AND incomeType <> 'TRANSFER';"
        )
        result = get_sql_from_db(sql)

        if result["income"] is None or ("income" in result and decimals.create_decimal(result["income"]) <= 0):
            lvl_1_users.append({
                "user_id": user["user_id"],
                "reg_time": user["time"],
                "username": get_sql_from_db(f"SELECT username FROM user_model WHERE id = {user['user_id']}")["username"],
                "income_for_all_time": 0
            })
        else:
            income = decimals.create_decimal(result["income"]) / 100 * 4
            if income - balance > 1000 or get_user_balance(user_id=user["user_id"]) - balance >= 10:
                income = balance / 100 * 4
            lvl_1_users.append({
                "user_id": user["user_id"],
                "reg_time": user["time"],
                "username": result["username"],
                "income_for_all_time": income
            })
    return lvl_1_users

def get_others_lvl(users: typing.List[typing.Dict], balance: decimal.Decimal) -> typing.List[typing.Dict]:
    others_lvl: typing.List[typing.Dict] = []
    for user_lvl in users:
        user = get_users_others_lvl(
            users=user_lvl["users"],
            lvl=user_lvl["lvl"],
            percent=user_lvl["percent"],
            balance=balance
        )
        others_lvl.append(user)
    return others_lvl

def get_users_others_lvl(users: typing.List[typing.Dict], lvl: int, percent: int, balance: decimal.Decimal) -> typing.Dict:
    income_for_lvl = 0
    time_now = int(datetime.timestamp(datetime.now()))
    for user in users:
        sql = (
            f"SELECT SUM(income) AS income FROM income_model "
            f"WHERE user_id = {user['user_id']} AND "
            f"AND time >= {user['time']} "
            f"AND time <= {time_now} "
            f"AND asset <> 'BNB'"
            f"AND incomeType <> 'TRANSFER';"
        )
        result = get_sql_from_db(sql)
        if result is not None and result != {}:
            income = decimals.create_decimal(result["income"]) / 100 * percent
            if income - balance >= 1000 or get_user_balance(user_id=user["user_id"]) - balance >= 10:
                income = balance / 100 * percent
            income_for_lvl += income
    return {
        "lvl": lvl,
        "user_count": len(users),
        "income_all_time": income_for_lvl
    }

def get_ref_info_by_user_id(user_id: int) -> typing.Dict:
    sql = f"SELECT referral_code, referrer, ref_users FROM referral_model WHERE user_id={user_id}"
    my_balance = get_user_balance(user_id)
    result = get_sql_from_db(sql)
    referral_code = result["referral_code"]

    lvl_1: typing.List = get_lvl_1(users=json.loads(result["ref_users"])["lvl_1"], balance=my_balance)
    others_lvl = get_others_lvl(users=[
        {
            "users": json.loads(result["ref_users"])["lvl_2"],
            "lvl": 2,
            "percent": 3
        },
        {
            "users": json.loads(result["ref_users"])["lvl_3"],
            "lvl": 3,
            "percent": 2
        },
        {
            "users": json.loads(result["ref_users"])["lvl_4"],
            "lvl": 4,
            "percent": 1
        },
    ], balance=my_balance)
    return {
        "referral_code": referral_code,
        "its_lvl_1": lvl_1,
        "its_others_lvl": others_lvl
    }