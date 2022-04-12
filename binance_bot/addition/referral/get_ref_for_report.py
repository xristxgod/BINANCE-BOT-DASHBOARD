import typing
import sqlite3
import json

from datetime import datetime

from addition.config import decimals, db_path
from addition.helper import dict_factory
from addition.referral.reg_user import get_sql_from_db
from addition.referral.get_ref import get_ref_info_by_user_id

from addition.sripts.add_ref_info import get_info

def get_report_v2(user_id: int, start: int, end: int):
    sql = (
        f"SELECT time, lvl "
        f"FROM referral_profit_model "
        f"WHERE user_id={user_id} "
        f"AND time >= {start} "
        f"AND time <= {end}"
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

# --------------------------------------------------------------------------------------------------------------------

def get_report_v2_to_day(user_id: int):
    t = int(datetime.timestamp(datetime.strptime(str(datetime.now().date()), '%Y-%m-%d')))
    return [{
        "time": str(datetime.fromtimestamp(t)),
        "lvl": get_info(user_id=user_id)
    }]