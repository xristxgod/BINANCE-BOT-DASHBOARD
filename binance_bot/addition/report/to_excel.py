import os
import typing

import pandas as pd
import datetime

from addition.config import EXCEL_FILE_PATH, logger

def write_to_excel(start: datetime, end: datetime, report: typing.List[typing.Dict]) -> typing.Union[bool, str]:
    try:
        if os.path.exists(EXCEL_FILE_PATH):
            os.remove(EXCEL_FILE_PATH)
            logger.error("EXCEL FILE DELETE")
        data_to_execl: typing.Dict = {
            "Username": [],
            "Balance": [],
            "Bots&Profit": [],
            "Withdraw": [],
            "Deposit": [],
            "Referral Profit": []
        }
        for rep in report:
            data_to_execl["Username"].append(rep["username"])
            data_to_execl["Balance"].append("{} USDT".format(rep["report"]["balance"]))
            data_to_execl["Bots&Profit"].append(__get_bots_and_profit(bots=rep["report"]["profit_period"]))
            data_to_execl["Withdraw"].append(__get_withdraw_or_deposit(data=rep["report"]["withdraw_history"]))
            data_to_execl["Deposit"].append(__get_withdraw_or_deposit(data=rep["report"]["deposit_history"]))
            data_to_execl["Referral Profit"].append(__get_referral_profit(referral=rep["report"]["referral_profit"]))
        df = pd.DataFrame(data_to_execl)
        df.to_excel(EXCEL_FILE_PATH, sheet_name=f'Report-{start}-{end}', index=True)
        return True
    except Exception as error:
        logger.error(f"{error}")
        return False

def __get_referral_profit(referral: typing.List[typing.Dict]):
    text = ""
    for ref in referral:
        text += f"{ref['time']}\n{__get_lvl(lvl=ref['lvl'])}\n"
    return text

def __get_lvl(lvl: typing.Dict):
    text = ""
    for num, income in lvl.items():
        text += f"{num} : {income} USDT\n"
    return text

def __get_withdraw_or_deposit(data: typing.List[typing.Dict]):
    text = ""
    for d in data:
        text += f"{d['time']} | {d['amount']} USDT\n"
    return text

def __get_bots_and_profit(bots: typing.List[typing.Dict]) -> str:
    text = ""
    for i, bot in enumerate(bots):
        text += f"{i+1}. {bot['name']} | {bot['income']} USDT\n"
    return text