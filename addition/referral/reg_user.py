import json
import sqlite3
import typing
from datetime import datetime

from addition.config import db_path
from addition.referral.ref import is_have
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

def post_sql_from_db(sql: str):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        return True
    except Exception as error:
        return False
    finally:
        if connection is not None:
            connection.close()

def search_by_ref_code(n_referral: str, user_id: int, lvl=1):
    get_sql = f"SELECT referral_code, referrer, ref_users FROM referral_model WHERE referral_code='{n_referral}'"
    result = get_sql_from_db(sql=get_sql)
    ref_users = json.loads(result["ref_users"])
    for i, k in ref_users.items():
        if is_have(ref_user=k, user_id=user_id):
            return True
    if lvl >= 4:
        ref_users[f"lvl_{4}"].append({
            "user_id": user_id,
            "time": int(datetime.timestamp(datetime.now()))
        })
    else:
        ref_users[f"lvl_{lvl}"].append({
            "user_id": user_id,
            "time": int(datetime.timestamp(datetime.now()))
        })
    post_sql = f"UPDATE referral_model SET ref_users='{json.dumps(ref_users)}' WHERE referral_code='{n_referral}'"
    status = post_sql_from_db(post_sql)
    if not status:
        raise Exception("Not add ref")
    if result["referrer"] is not None:
        return search_by_ref_code(n_referral=result["referrer"], user_id=user_id, lvl=lvl + 1)