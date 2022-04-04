import typing

from src.client import client_post
from config import decimals

async def get_username_by_chat_id(chat_id: int) -> typing.Union[typing.Dict, None]:
    response: typing.Dict = await client_post(chat_id=chat_id, url="/get-user-by-chat-id")
    if "message" in response and isinstance(response["message"], str) and response["message"] != "Not found":
        if "is_admin" in response and response["is_admin"]:
            return {"username": response["message"], "admin": True}
        return {"username": response["message"], "admin": False}
    return None

async def get_balance_by_chat_id(chat_id: int) -> typing.Union[typing.Dict, int]:
    response: typing.Dict = await client_post(chat_id=chat_id, url="/get-balance-by-chat-id")
    if "message" in response and isinstance(response["message"], str) and response["message"] != "Not found":
        return {"balance": decimals.create_decimal(response["message"])}
    return {"balance": 0}

async def reset_password_api_route_by_chat_id(chat_id: int) -> typing.Dict:
    response: typing.Dict = await client_post(chat_id=chat_id, url="/reset-password-api-route")
    return {"status": response["message"]}

async def get_all_balance_by_admin_id(chat_id: int) -> str:
    response: typing.Dict = await client_post(chat_id=chat_id, url="/get-info_s-by-chat-id")
    text = ""
    if "message" in response and isinstance(response["message"], str) and response["message"] != "Not found":
        for res in response["message"]:
            text += f"Username: {res['username']} | Balance: {res['balance']}\n"
        return text
    return text
