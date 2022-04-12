import sqlite3
import typing
import decimal
from datetime import datetime

from addition.utils import timeranges, dict_factory
from addition.config import decimals, db_path

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
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        sql = (
            f'SELECT SUM(income) FROM income_model '
            f'WHERE asset <> "BNB" '
            f'AND incomeType <> "TRANSFER" '
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
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        return[i[0] for i in cursor.execute(f"SELECT api_label FROM account_model WHERE user_id={user_id}").fetchall()]
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def inset_new_balance(new_balance: str, user_id: int) -> bool:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE user_model SET budget={new_balance} WHERE id={user_id}"
        )
        connection.commit()
        return True
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_user_balance(user_id: int) -> decimal.Decimal:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        return decimals.create_decimal(cursor.execute(
            f"SELECT budget FROM user_model WHERE id='{user_id}'"
        ).fetchone()[0])
    except Exception as error:
        return decimals.create_decimal("0")
    finally:
        if connection is not None:
            connection.close()

def inset_withdraw(ins_time: int, amount: str, user_id: int):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(
            f"INSERT INTO withdraw_model (time, amount, user_id) VALUES ({ins_time}, '{amount}', {user_id})"
        )
        connection.commit()
        return True
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_user_info_by_id(user_id: int):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        return cursor.execute(
            f"SELECT username, email_address AS email FROM user_model WHERE id={user_id}"
        ).fetchone()
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_user_tg_id_by_user_id(user_id: int):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        return cursor.execute(
            f"SELECT chat_id FROM telegram_bot_model WHERE user_id={user_id}"
        ).fetchone()[0]
    except Exception as error:
        return None
    finally:
        if connection is not None:
            connection.close()

def get_is_have_balance(user_id: int) -> bool:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        stat = cursor.execute(
            f"SELECT SUM(totalWalletBalance) <= 0 AS balance_bots FROM account_model WHERE user_id = {user_id}"
        ).fetchone()
        if stat is None \
                or ("balance_bots" in stat and stat["balance_bots"] is None) \
                or ("balance_bots" in stat and stat["balance_bots"]):
            return True
        status = cursor.execute(
            (
                "SELECT SUM(account_model.totalWalletBalance) / 100 * 5 <= user_model.budget AS is_min_balance "
                "FROM account_model, user_model "
                f"WHERE user_model.id = {user_id} AND account_model.user_id = {user_id};"
            )
        ).fetchone()["is_min_balance"]
        return True if status is None or bool(status) else False
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_chat_id_by_user_id(user_id: int) -> typing.Dict:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        result = cursor.execute(
            (
                f"SELECT chat_id FROM telegram_bot_model WHERE user_id = {user_id};"
            )
        ).fetchone()
        if result is None:
            return {}
        return result
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_user_info_by_user_id(user_id: int) -> typing.Dict:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        return cursor.execute(
            (
                "SELECT id, username, email_address AS email "
                "FROM user_model "
                f"WHERE id = {user_id};"
            )
        ).fetchone()
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_capital():
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        return cursor.execute("SELECT SUM(budget) as totalCapital FROM user_model WHERE status='active' AND is_admin=0").fetchone()
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_pnl_all_time():
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        data = cursor.execute(
            f'SELECT SUM(income) as totalIncome FROM income_model WHERE asset <> "BNB" AND incomeType <> "TRANSFER";'
        ).fetchone()
        return data
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_unrealized_pnl_all_time():
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        data = cursor.execute(
            f'SELECT SUM(unrealizedProfit) as totalUnrealizedPNL FROM positions_model;'
        ).fetchone()
        return data
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_user_budget_by_api_label(api_label: str):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        data = cursor.execute(
            f"SELECT budget FROM user_model WHERE id=(SELECT user_id FROM account_model WHERE api_label='{api_label}');"
        ).fetchone()
        return decimals.create_decimal(data["budget"])
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_users_id() -> typing.List:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        return [i[0] for i in cursor.execute("SELECT id FROM user_model WHERE status='active' AND is_admin=0").fetchall()]
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_users_info_by_ids_list(ids: typing.Tuple[int]) -> typing.Dict:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        user_info = cursor.execute((
            f"SELECT user_model.id, user_model.username, user_model.budget AS balance, user_model.email_address AS email "
            f"FROM user_model WHERE user_model.id IN {ids};"
        )).fetchall()
        # api_info = cursor.execute((
        #     f"SELECT account_model.user_id, account_model.api_label, account_model.totalWalletBalance "
        #     f"FROM account_model WHERE account_model.user_id IN {ids};"
        # )).fetchall()
        income_info = []
        for _id in ids:
            income_info.append(cursor.execute((
                f"SELECT income_model.api_label, SUM(income_model.income) as totalIncome, income_model.user_id "
                f"FROM income_model WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' AND income_model.user_id = {_id};"
            )).fetchone())
        return {
            "userInfo": user_info,
            # "apiInfo": api_info,
            "incomeInfo": income_info
        }
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_position_info_by_api_label_and_user_id(api_label: str, user_id: int, coin: str) -> typing.Dict:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        return cursor.execute((
            f"SELECT leverage, entryPrice "
            f"FROM positions_model "
            f"WHERE api_label='{api_label}' AND user_id={user_id} "
            f"AND symbol='{coin}'"
        )).fetchone()
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()
