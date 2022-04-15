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
        return cursor.execute("SELECT SUM(totalWalletBalance) as totalCapital FROM account_model").fetchone()
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

def get_username_by_id(user_id: int):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        return cursor.execute(
            f'SELECT username FROM user_model WHERE id = {user_id}'
        ).fetchone()[0]
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

# <<<---------------------------------->>> USER STATISTIC DASHBOARD <<<---------------------------------------------->>>

def get_total_wallet_balance_by_users_ids(users_ids: typing.Tuple[int]) -> float:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if len(users_ids) == 1:
            data = cursor.execute(
                f"SELECT totalWalletBalance FROM account_model WHERE user_id={users_ids[0]};"
            ).fetchall()
        else:
            data = cursor.execute(
                f"SELECT totalWalletBalance FROM account_model WHERE user_id IN {users_ids};"
            ).fetchall()
        balance = 0
        for d in data:
            if d[0] is not None and not isinstance(d, str):
                balance += d[0]
        return balance
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_total_sum_income_by_users_ids(users_ids: typing.Tuple[int]) -> float:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if len(users_ids) == 1:
            data = cursor.execute((
                f"SELECT SUM(income) FROM income_model "
                f"WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' AND user_id={users_ids[0]};"
            )).fetchall()
        else:
            data = cursor.execute((
                f"SELECT SUM(income) FROM income_model "
                f"WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' AND user_id IN {users_ids};"
            )).fetchall()
        return sum([d[0] for d in data]) if data[0][0] is not None else None
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_time_sum_income_by_users_ids(users_ids: typing.Tuple[int], start: int, end: int) -> float:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if len(users_ids) == 1:
            data = cursor.execute((
                f"SELECT SUM(income) FROM income_model "
                f"WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' "
                f"AND time >= {start} AND time <= {end} "
                f"AND user_id={users_ids[0]};"
            )).fetchall()
        else:
            data = cursor.execute((
                f"SELECT SUM(income) FROM income_model "
                f"WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' "
                f"AND time >= {start} AND time <= {end} "
                f"AND user_id IN {users_ids};"
            )).fetchall()
        return sum([d[0] for d in data]) if data[0][0] is not None else None
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_total_unrealized_pnl_by_users_ids(users_ids: typing.Tuple[int]) -> float:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if len(users_ids) == 1:
            data = cursor.execute(
                f"SELECT SUM(unrealizedProfit) FROM positions_model WHERE user_id={users_ids[0]};"
            ).fetchall()
        else:
            data = cursor.execute(
                f"SELECT SUM(unrealizedProfit) FROM positions_model WHERE user_id IN {users_ids};"
            ).fetchall()
        return sum([d[0] for d in data]) if data[0][0] is not None else None
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_all_fees_by_users_ids(users_ids: typing.Tuple[int]) -> typing.Tuple:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if len(users_ids) == 1:
            data = cursor.execute((
                f"SELECT SUM(income), asset FROM "
                f"income_model WHERE incomeType ='COMMISSION' AND user_id={users_ids[0]} "
                f"GROUP BY asset;"
            )).fetchall()
        else:
            data = cursor.execute((
                f"SELECT SUM(income), asset FROM "
                f"income_model WHERE incomeType ='COMMISSION' AND user_id IN {users_ids} "
                f"GROUP BY asset;"
            )).fetchall()
        return data
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_income_by_date_and_users_ids(users_ids: typing.Tuple[int], start: int, end: int) -> typing.List[typing.Tuple]:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if len(users_ids) == 1:
            return cursor.execute((
                f"SELECT DATE(time / 1000, 'unixepoch') AS Date, SUM(income) AS inc FROM income_model "
                f"WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' "
                f"AND time >= {start} AND time <= {end} "
                f"AND user_id={users_ids[0]} "
                f"GROUP BY Date;"
            )).fetchall()
        else:
            return cursor.execute((
                f"SELECT DATE(time / 1000, 'unixepoch') AS Date, SUM(income) AS inc FROM income_model "
                f"WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' "
                f"AND time >= {start} AND time <= {end} "
                f"AND user_id IN {users_ids} "
                f"GROUP BY Date;"
            )).fetchall()
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_income_by_symbol_and_users_ids(users_ids: typing.Tuple[int], start: int, end: int) -> typing.List[typing.Tuple]:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if len(users_ids) == 1:
            return cursor.execute((
                f"SELECT SUM(income) AS inc, symbol FROM income_model "
                f"WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' "
                f"AND time >= {start} AND time <= {end} "
                f"AND user_id={users_ids[0]} "
                f"GROUP BY symbol ORDER BY inc DESC;"
            )).fetchall()
        else:
            return cursor.execute((
                f"SELECT SUM(income) AS inc, symbol FROM income_model "
                f"WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' "
                f"AND time >= {start} AND time <= {end} "
                f"AND user_id IN {users_ids} "
                f"GROUP BY symbol ORDER BY inc DESC;"
            )).fetchall()
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_users_sum_budget_by_ids(users_ids: typing.Tuple[int]) -> float:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if len(users_ids) == 1:
            data = cursor.execute(
                f"SELECT totalWalletBalance FROM account_model WHERE user_id={users_ids[0]};"
            ).fetchone()
        else:
            data = cursor.execute(
                f"SELECT SUM(totalWalletBalance) FROM account_model WHERE user_id IN {users_ids};"
            ).fetchone()
        return decimals.create_decimal(data[0]) if data[0] is not None else 0
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_custom_frame_by_users_ids(users_ids: typing.Tuple[int], start: int, end: int) -> float:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if len(users_ids) == 1:
            data = cursor.execute((
                f"SELECT SUM(income) AS inc, symbol FROM income_model "
                f"WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' "
                f"AND time >= {start} AND time <= {end} "
                f"AND user_id={users_ids[0]} "
                f"GROUP BY symbol ORDER BY inc DESC;"
            )).fetchone()
        else:
            data = cursor.execute((
                f"SELECT SUM(income) FROM income_model "
                f"WHERE asset <> 'BNB' AND incomeType <> 'TRANSFER' "
                f"AND time >= {start} AND time <= {end} "
                f"AND user_id IN {users_ids};"
            )).fetchone()
        return data[0]
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

# <<<---------------------------------->>> USER STATISTIC CARD <<<--------------------------------------------------->>>

def __get_income_by_api_label(api_label: str, user_id: int):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        data = cursor.execute(
            f"SELECT SUM(income) FROM income_model WHERE api_label = '{api_label}' AND user_id = {user_id}"
        ).fetchone()
        return "%.4f" % decimals.create_decimal(data[0]) if data[0] is not None else 0
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_users_info_by_users_ids(users_ids: typing.List[int]) -> typing.List:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        result = []
        for user_id in users_ids:
            data = cursor.execute((
                f"SELECT user_model.username, user_model.budget, user_model.email_address AS email, "
                f"account_model.api_label, account_model.totalWalletBalance "
                f"FROM user_model, account_model "
                f"WHERE user_model.id={user_id} AND account_model.user_id={user_id};"
            )).fetchall()
            if len(data) == 0:
                data = cursor.execute(
                    f"SELECT username, budget, email_address AS email FROM user_model WHERE id={user_id}"
                ).fetchone()
                result.append({
                    "username": data["username"],
                    "balanceUSDT": data["budget"],
                    "email": data["email"],
                    "totalBalanceBinance": 0,
                    "apisLabel": []
                })
                continue
            user_data = {
                "username": data[0]["username"],
                "balanceUSDT": data[0]["budget"],
                "email": data[0]["email"],
                "totalBalanceBinance": 0,
                "apisLabel": []
            }
            apis = []
            for api in data:
                apis.append(api["api_label"])
                user_data["totalBalanceBinance"] += decimals.create_decimal(api["totalWalletBalance"])
                user_data["apisLabel"].append({
                    "apiLabelName": api["api_label"],
                    "totalIncome": __get_income_by_api_label(api["api_label"], user_id=user_id),
                    "balanceBinance": "%.4f" % decimals.create_decimal(api["totalWalletBalance"])
                })
            result.append(user_data)
        return result
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()