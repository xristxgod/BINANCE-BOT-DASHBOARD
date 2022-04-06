import aiohttp
import asyncio
from datetime import datetime
from addition.config import symbol

from addition.db_wallet import get_is_have_balance, get_chat_id_by_user_id, get_user_info_by_user_id, get_users
from addition.json_db import json_db
from addition.config import ADMIN_IDS, TOKEN, logger

async def send_to_bots(user_id: int):
    user_chat_id = get_chat_id_by_user_id(user_id=user_id)
    user_info = get_user_info_by_user_id(user_id=user_id)
    text_for_admin = (
        f"{symbol['dec']} The user has less than 5% on the balance\n"
        f"ID: {user_info['id']}\n"
        f"Username: {user_info['username']}\n"
        f"Email: {user_info['email']}"
    )
    text_for_user = (
        f"{symbol['dec']} You have less than 5% on your balance\n"
        "The bot has been disabled\n"
        "Top up your balance!!!"
    )
    await send_to_admin_bot(text=text_for_admin)
    if user_chat_id is not None and user_chat_id != {} and user_chat_id["chat_id"]:
        await send_to_user_bot(text=text_for_user, chat_id=user_chat_id["chat_id"])
    return True

async def send_to_admin_bot(text: str):
    try:
        async with aiohttp.ClientSession() as session:
            for user_id in ADMIN_IDS:
                if user_id == "":
                    continue
                # Send a request to the bot.
                async with session.get(
                        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                        params={
                            # You can get it from @username_to_id_bot.
                            "chat_id": user_id,
                            "text": text,
                            # So that you can customize the text.
                            "parse_mode": "html"
                        }
                ) as response:
                    if not response.ok:
                        logger.error(f'MESSAGE WAS NOT SENT TO ADMIN: {text}')
                    else:
                        logger.error(f'MESSAGE HAS BEEN SENT TO ADMIN: {text}.')
    except Exception as error:
        logger.error(f"ERROR SEND TO BOT: {error}")

async def send_to_user_bot(text: str, chat_id: int):
    try:
        async with aiohttp.ClientSession() as session:
            # Send a request to the bot.
            async with session.get(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    params={
                        # You can get it from @username_to_id_bot.
                        "chat_id": chat_id,
                        "text": text,
                        # So that you can customize the text.
                        "parse_mode": "html"
                    }
            ) as response:
                if not response.ok:
                    logger.error(f'MESSAGE WAS NOT SENT TO USER CHAT ID {chat_id}: {text}. {await response.text()}')
                else:
                    logger.error(f'MESSAGE HAS BEEN SENT TO USER CHAT ID {chat_id}: {text}.')
    except Exception as error:
        logger.error(f"ERROR SEND TO BOT: {error}")

# <<------------------------------------------------------------------------------------------------------------------>>

async def check_balance(user_id: int):
    if get_is_have_balance(user_id=user_id):
        return await json_db.is_have_user_id(user_id=user_id)
    else:
        return await send_to_bots(user_id) if await json_db.insert_user_if_not_balance(user_id=user_id) else False

async def run():
    logger.error("START BOT\n")
    logger.error(f"START ITERATION: {datetime.now()}")
    await asyncio.gather(*[
        check_balance(user_id=user["id"])
        for user in get_users()
    ])
    logger.error(f"END ITERATION: {datetime.now()}\n")
    logger.error("END BOT")

def main() -> bool:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())
        return True
    except Exception as error:
        logger.error(f"{error}")
        return False

if __name__ == '__main__':
    main()