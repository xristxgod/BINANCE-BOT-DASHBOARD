import sqlite3
from addition.config import db_path

def is_ref(referrer: str) -> bool:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        result = cursor.execute(f"SELECT referral_code FROM referral_model WHERE referral_code='{referrer}'").fetchone()
        if result:
            return True
        else:
            return False
    except Exception as error:
        raise TypeError
    finally:
        if connection is not None:
            connection.close()

def is_have(user_id: int, ref_user):
    for i in ref_user:
        if i["user_id"] == user_id:
            return True
    return False