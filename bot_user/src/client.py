import typing

import aiohttp

from config import API_URL

async def client_post(chat_id: int, url: str) -> typing.Dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL+url, json={"chatID": chat_id}) as resp:
            response = await resp.json()
    return response