import json
import sqlite3
import typing
import decimal
from datetime import datetime

from addition.config import db_path, decimals
from addition.utils import dict_factory

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
            f"SELECT user_model.username, SUM(income_model.income) AS income "
            f"FROM user_model, income_model "
            f"WHERE user_model.id = {user['user_id']} "
            f"AND income_model.user_id = {user['user_id']} "
            f"AND income_model.time >= {user['time']} "
            f"AND income_model.time <= {time_now} "
            f"AND income_model.asset <> 'BNB'"
            f"AND income_model.incomeType <> 'TRANSFER';"
        )
        result = get_sql_from_db(sql)
        if result["username"] is None and result["income"] is None:
            lvl_1_users.append({
                "user_id": user["user_id"],
                "reg_time": user["time"],
                "username": get_sql_from_db(f"SELECT username FROM user_model WHERE id = {user['user_id']}")["username"],
                "income_for_all_time": 0
            })
        else:
            income = decimals.create_decimal(result["income"]) / 100 * 4 if decimals.create_decimal(result["income"]) > 0 else 0
<<<<<<< HEAD

=======
            
>>>>>>> 32a942661ffae61776fb7192a0e03f5cbec50801
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
            f"SELECT SUM(income) AS income"
            f"FROM income_model "
            f"WHERE user_id = {user['user_id']} AND "
            f"AND income_model.time >= {user['time']} "
            f"AND income_model.time <= {time_now} "
            f"AND income_model.asset <> 'BNB'"
            f"AND income_model.incomeType <> 'TRANSFER';"
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

def get_user_balance(user_id: int) -> decimal.Decimal:
    sql = f"SELECT SUM(totalWalletBalance) as balance FROM account_model WHERE user_id={user_id}"
    result = get_sql_from_db(sql)
    return decimals.create_decimal(result["balance"]) if result["balance"] is not None else 0

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