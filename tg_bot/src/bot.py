import typing

import aiogram
from aiogram import types

from src.service import (
    get_username_by_chat_id,
    get_balance_by_chat_id,
    reset_password_api_route_by_chat_id,
    get_all_balance_by_admin_id
)
from config import TOKEN, SYMBOLS, logger

bot = aiogram.Bot(token=TOKEN)
dp = aiogram.Dispatcher(bot)

@dp.message_handler(commands=["help"])
async def send_welcome_helo(message: types.Message):
    await message.answer(
        ("<b>Welcome!!\n"
         "This bot only works with mybot.tech users.</b>"),
        parse_mode=types.ParseMode.HTML
    )

@dp.message_handler(commands=["start"])
async def send_welcome_start(message: types.Message):
    logger.error("COMMAND: /start")
    username = await get_username_by_chat_id(chat_id=message.from_user.id)
    if username is not None:
        if username["admin"]:
            keyboard_markup = aiogram.types.InlineKeyboardMarkup()
            user_id_btn = aiogram.types.InlineKeyboardButton(
                f'{SYMBOLS["moneyBank"]}Get the balance of all users {SYMBOLS["moneyBank"]}',
                callback_data='all_balance',
            )
            keyboard_markup.row(user_id_btn)
            await message.answer(
                f"{SYMBOLS['admin']} <b>Welcome, {username['username']}</b>",
                reply_markup=keyboard_markup,
                parse_mode=types.ParseMode.HTML
            )
        else:
            keyboard_markup = aiogram.types.InlineKeyboardMarkup()
            balance = aiogram.types.InlineKeyboardButton(
                f'{SYMBOLS["creditCard"]} Balance {SYMBOLS["creditCard"]}',
                callback_data='balance'
            )
            resetting_password = aiogram.types.InlineKeyboardButton(
                f'{SYMBOLS["lock"]} Resetting password {SYMBOLS["unlock"]}',
                callback_data='resetting_password'
            )
            keyboard_markup.row(balance, resetting_password)
            await message.answer(
                f"{SYMBOLS['user']} <b>Welcome, {username['username']}</b>",
                reply_markup=keyboard_markup,
                parse_mode=types.ParseMode.HTML
            )
    else:
        await message.answer(
            ("<b>Welcome!!!\n"
             "This bot only works with mybot.tech users.\n"
             "I couldn't find your ID in the system.\n"
             "If you are in the system, enter your email.\n"
             "I will send you the code after which you can safely use my services.</b>"),
            parse_mode=types.ParseMode.HTML
        )

@dp.callback_query_handler(lambda c: c.data == 'balance')
async def get_user_balance(callback_query: types.CallbackQuery):
    logger.error(f"/start user: {callback_query.from_user.id} func get user balance")
    balance: typing.Dict = await get_balance_by_chat_id(chat_id=callback_query.from_user.id)
    await callback_query.answer(f"Balance: {balance['balance']}", True)

@dp.callback_query_handler(lambda c: c.data == 'resetting_password')
async def get_resetting_password(callback_query: types.CallbackQuery):
    logger.error(f"/start user: {callback_query.from_user.id} func get resetting password")
    status: typing.Dict = await reset_password_api_route_by_chat_id(chat_id=callback_query.from_user.id)
    await callback_query.answer(f"{status['status']}", True)

@dp.callback_query_handler(lambda c: c.data == 'all_balance')
async def get_all_balance(callback_query: types.CallbackQuery):
    logger.error(f"/start admin: {callback_query.from_user.id} func get all balance")
    balances: str = await get_all_balance_by_admin_id(chat_id=callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, balances, parse_mode=types.ParseMode.HTML)