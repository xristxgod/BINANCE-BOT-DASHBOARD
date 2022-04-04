import json
import typing
from addition.config import USERS_FILE, logger


class JsonDB:

    @staticmethod
    def get_file():
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                return json.loads(file.read())
        except json.decoder.JSONDecodeError as error:
            return []

    @staticmethod
    def post_file(values: typing.List[typing.Dict]):
        with open(USERS_FILE, "w", encoding="utf-8") as file:
            file.write(json.dumps(values))
        return True

    @staticmethod
    async def is_have_user_id(user_id: int):
        values: typing.List[typing.Dict] = JsonDB.get_file()
        for value in values:
            if value["id"] == user_id:
                logger.error(f"THE USER ID={user_id} HAS BALANCE")
                JsonDB.post_file([value for value in values if value['id'] != user_id])
                return True                                 # Send and say that the balance has appeared
        else:
            return False                                    # Not send

    @staticmethod
    async def insert_user_if_not_balance(user_id: int):
        values: typing.List[typing.Dict] = JsonDB.get_file()
        for value in values:
            if value["id"] == user_id:
                return False                                        # Not send
        else:
            logger.error(f"THE USER ID={user_id} NOT BALANCE")
            values.append({"id": user_id, "status": False})
            return JsonDB.post_file(values=values)             # Send and say that there is no balance

json_db = JsonDB