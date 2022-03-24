import json
import typing
from datetime import datetime

from addition.config import decimals
from addition.referral.reg_user import post_sql_from_db
from addition.referral.get_ref import get_ref_info_by_user_id
from addition.db_wallet import get_users

def get_lvl_1(info: typing.List[typing.Dict]):
    income = 0
    for i in info:
        income += decimals.create_decimal(i["income_for_all_time"])
    return "%.8f" % income

def get_other_lvl(info: typing.List[typing.Dict]):
    lvl = {}
    for i in info:
        if i["lvl"] == 2:
            lvl["lvl_2"] = "%.8f" % decimals.create_decimal(i["income_all_time"])
        if i["lvl"] == 3:
            lvl["lvl_3"] = "%.8f" % decimals.create_decimal(i["income_all_time"])
        if i["lvl"] == 4:
            lvl["lvl_4"] = "%.8f" % decimals.create_decimal(i["income_all_time"])
    return lvl

def get_info(user_id: int) -> typing.Dict:
    info = get_ref_info_by_user_id(user_id=user_id)
    return {
        "lvl_1": get_lvl_1(info["its_lvl_1"]),
        **get_other_lvl(info["its_others_lvl"])
    }

def insert_info(info: typing.Dict, user_id: int):
    sql = (
        f"INSERT INTO referral_profit_model (lvl, time, user_id) "
        f"VALUES ('{json.dumps(info)}', {int(datetime.timestamp(datetime.strptime(str(datetime.now().date()), '%Y-%m-%d')))}, {user_id})"
    )
    return post_sql_from_db(sql)

def get_ref_info_to_day():
    users = get_users()
    for user in users:
        try:
            info = get_info(user_id=user["id"])
            insert_info(info, user_id=user["id"])
        except Exception as error:
            if str(error) == "'NoneType' object is not subscriptable":
                continue
            else:
                raise error

def main():
    get_ref_info_to_day()

if __name__ == '__main__':
    main()