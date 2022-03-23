import sqlite3
import typing
import decimal
from datetime import datetime

from addition.utils import timeranges
from addition.config import decimals, db_path

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_users() -> typing.List[typing.Dict]:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        return cursor.execute("SELECT * FROM user_model WHERE status='active' AND is_admin=0").fetchall()
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

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

def get_profit_today_by_api_label(api_label: str) -> typing.Union[decimal.Decimal, int]:
    ranges = timeranges()
    today_start = (
            datetime.combine(datetime.fromisoformat(ranges[0][0]), datetime.min.time()).timestamp()
            * 1000
    )
    today_end = (
            datetime.combine(datetime.fromisoformat(ranges[0][1]), datetime.max.time()).timestamp()
            * 1000
    )
    connection = None
    try:
        connection = sqlite3.connect("../database.db")
        cursor = connection.cursor()
        sql = (
            f'SELECT SUM(income) FROM income_model '
            f'WHERE asset <> "USDT" '
            f'AND incomeType <> "REALIZED_PNL" '
            f'AND time >= {today_start} '
            f'AND time <= {today_end} '
            f'AND api_label="{api_label}"'
        )
        profit_today = cursor.execute(sql).fetchone()[0]
        if profit_today is not None:
            return decimals.create_decimal(profit_today)
        return 0
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_api_label_list_by_user_id(user_id: int) -> typing.List:
    connection = None
    try:
        connection = sqlite3.connect("../database.db")
        cursor = connection.cursor()
        return[i[0] for i in cursor.execute(f"SELECT api_label FROM account_model WHERE user_id={user_id}").fetchall()]
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def inset_new_balance_by_api_label(new_balance: str, api_label: str, user_id: int) -> bool:
    connection = None
    try:
        connection = sqlite3.connect("../database.db")
        cursor = connection.cursor()
        cursor.execute(
            (
                f"INSERT INTO account_model(totalWalletBalance) "
                f"VALUES ({float(new_balance)}) "
                f"WHERE api_label='{api_label}' "
                f"AND user_id={user_id}"
            )
        )
        connection.commit()
        return True
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()
