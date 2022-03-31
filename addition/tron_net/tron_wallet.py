import sqlite3
import typing

from addition.tron_net.generate_wallet import generate_usdt_trc20
from addition.config import db_path
from addition.utils import dict_factory

def get_wallet_by_user_id(user_id: id) -> typing.Dict:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        wallet = cursor.execute(
            f"SELECT address, status, last_activate_time FROM user_wallet_model WHERE user_id={user_id}"
        ).fetchone()
        if wallet is None:
            return create_wallet_if_not(user_id=user_id)
        return wallet
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def create_wallet_if_not(user_id: int) -> typing.Dict:
    wallet = generate_usdt_trc20()
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(
            (
                f"INSERT INTO user_wallet_model (address, private_key, status, last_activate_time, user_id) "
                f"VALUES ('{wallet['address']}', '{wallet['private_key']}', false, 0, {user_id})"
            )
        ).fetchone()
        connection.commit()
        return {
            "address": wallet["address"],
            "status": False,
            "last_activate_time": 0
        }
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def get_wallet_info_by_user_id(user_id: id) -> typing.Dict:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        return cursor.execute(
            f"SELECT address, private_key FROM user_wallet_model WHERE user_id={user_id}"
        ).fetchone()
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def insert_transaction(tx_id: str, timestamp: int, user_id: int, amount: int):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute((
            f"INSERT INTO tron_transaction_model (time, tx_id, user_id, amount) "
            f"VALUES ({timestamp}, '{tx_id}', {user_id}, {int(amount)})"
        )).fetchone()
        connection.commit()
        return True
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def update_status_sub(user_id: int, status: bool, last_time: int = None):
    connection = None
    try:
        sql = f"UPDATE user_wallet_model SET status={1 if status else 0}"
        if last_time is not None:
            sql += f", last_activate_time={last_time}"
        sql += f" WHERE user_id={user_id};"
        print(sql)
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        return True
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()

def update_balance(user_id: int, balance: int):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE user_model SET budget=budget + {balance} WHERE id={user_id}"
        )
        connection.commit()
        return True
    except Exception as error:
        raise error
    finally:
        if connection is not None:
            connection.close()
