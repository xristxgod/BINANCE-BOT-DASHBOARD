# https://github.com/binance/binance-signature-examples
from __future__ import annotations
import datetime
import hashlib
import hmac
import sqlite3
import threading
import time
from datetime import timedelta
from sqlite3 import Error
from urllib.parse import urlencode
from futuresboard.db_manager import db
from futuresboard.models import *
from CredentialManager import CredentialManager
from flask_login import login_user, logout_user, login_required, current_user

import requests
from flask import current_app

from addition.config import decimals

MIN_SCRAPE_PERIOD_SEC = 1
LAST_SCRAPE_TIME_SEC = 0


class HTTPRequestError(Exception):

    def __init__(self, url, code, msg=None):
        self.url = url
        self.code = code
        self.msg = msg

    def __str__(self) -> str:
        """
        Convert the exception into a printable string
        """
        return f"Request to {self.url!r} failed. Code: {self.code}; Message: {self.msg}"


def auto_scrape(app):
    thread = threading.Thread(target=_auto_scrape, args=(app,))
    thread.daemon = True
    thread.start()


def _auto_scrape(app):
    with app.app_context():
        interval = app.config["AUTO_SCRAPE_INTERVAL"]
        while True:
            app.logger.info("Auto scrape routines starting")
            scrape(app=app)
            app.logger.info("Auto scrape routines terminated. Sleeping %s seconds...", interval)
            time.sleep(interval)

def get_one_mounth_ago():
    today = datetime.datetime.today()
    if today.month == 1:
        one_month_ago = today.replace(year=today.year - 1, month=12)
    else:
        extra_days = 0
        while True:
            try:
                one_month_ago = today.replace(month=today.month - 1, day=today.day - extra_days)
                break
            except ValueError:
                extra_days += 1
    return one_month_ago


def hashing(query_string, secret):
    return hmac.new(
        secret.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def get_timestamp():
    return int(time.time() * 1000)


def dispatch_request(active_api_label, http_method): 
    session = requests.Session()
    session.headers.update(
        {
            "Content-Type": "application/json;charset=utf-8",
            "X-MBX-APIKEY": CredentialManager.get_credentials(active_api_label)['apiKey'] if current_user.is_admin else CredentialManager.get_credentials(active_api_label, current_user.username)['apiKey'],
        }
    )
    return {
        "GET": session.get,
        "DELETE": session.delete,
        "PUT": session.put,
        "POST": session.post,
    }.get(http_method, "GET")


# used for sending request requires the signature
def send_signed_request(active_api_label, http_method, url_path, payload={}):
    query_string = urlencode(payload)
    if current_user.is_admin:
        secret = CredentialManager.get_credentials(active_api_label)['secret']
    else:
        secret = CredentialManager.get_credentials(active_api_label, current_user.username)['secret']
    # replace single quote to double quote
    query_string = query_string.replace("%27", "%22")
    if query_string:
        query_string = f"{query_string}&timestamp={get_timestamp()}"
    else:
        query_string = f"timestamp={get_timestamp()}"

    url = (
        current_app.config["API_BASE_URL"]
        +url_path
        +"?"
        +query_string
        +"&signature="
        +hashing(query_string, secret)
    )
    # print("{} {}".format(http_method, url))
    params = {"url": url, "params": {}}
    response = dispatch_request(active_api_label, http_method)(**params)
    headers = response.headers
    json_response = response.json()
    if "code" in json_response:
        raise HTTPRequestError(url=url, code=json_response["code"], msg=json_response["msg"])
    return headers, json_response


# used for sending public data request
def send_public_request(url_path, payload={}):
    query_string = urlencode(payload, True)
    url = current_app.config["API_BASE_URL"] + url_path
    if query_string:
        url = url + "?" + query_string
    # print("{}".format(url))
    response = dispatch_request("GET")(url=url)
    headers = response.headers
    json_response = response.json()
    if "code" in json_response:
        raise HTTPRequestError(url=url, code=json_response["code"], msg=json_response["msg"])
    return headers, json_response


def db_setup():
    db.create_all()
    pass


# income interactions
def create_income(income_data, active_api_label):
    tranId, symbol, incomeType, income, asset, info, time, tradeId = income_data
    income = IncomeModel(\
                         api_label=active_api_label, \
                         user_id=current_user.id, \
                         tranId=tranId, \
                         symbol=symbol, \
                         incomeType=incomeType, \
                         income=income, \
                         asset=asset, \
                         info=info, \
                         time=time, \
                         tradeId=tradeId)
    db.session.add(income)
    pass


def select_latest_income(active_api_label):
    income = IncomeModel.query.filter_by(api_label=active_api_label, user_id=current_user.id).order_by(IncomeModel.time.desc()).limit(1).first()
    return income


# position interactions
def create_position(position_data, active_api_label):
    unrealizedProfit, leverage, entryPrice, positionAmt, symbol, positionSide = position_data
    position = PositionsModel(symbol=symbol, \
                              api_label=active_api_label, \
                              user_id=current_user.id, \
                              leverage=leverage, \
                              entryPrice=entryPrice, \
                              positionAmt=positionAmt, \
                              positionSide=positionSide, \
                              unrealizedProfit=unrealizedProfit)
    db.session.add(position)
    pass 


def update_position(position_data, active_api_label):
    unrealizedProfit, leverage, entryPrice, positionAmt, symbol, positionSide = position_data
    position = PositionsModel.query.filter_by(\
                                              symbol=symbol, \
                                              api_label=active_api_label, \
                                              user_id=current_user.id, \
                                              leverage=leverage, \
                                              entryPrice=entryPrice, \
                                              positionAmt=positionAmt, \
                                              positionSide=positionSide).first()
    if position != None:
        position.unrealizedProfit = unrealizedProfit


def select_position(symbol, active_api_label, pos_side):
    position = PositionsModel.query.filter_by(symbol=symbol, positionSide=pos_side, api_label=active_api_label, user_id=current_user.id).first()
    return position


def delete_all_positions(active_api_label):
    positions = PositionsModel.query.filter_by(api_label=active_api_label, user_id=current_user.id).all()
    if len(positions) > 0:
        for position in positions:
            db.session.delete(position)
    db.session.commit()
    pass 


# account interactions
def create_account(account_data, active_api_label):
    totalWalletBalance, totalUnrealizedProfit, totalMarginBalance, availableBalance, maxWithdrawAmount, = account_data
    account = AccountModel(
                           api_label=active_api_label, \
                           user_id=current_user.id, \
                           totalWalletBalance=totalWalletBalance, \
                           totalUnrealizedProfit=totalUnrealizedProfit, \
                           totalMarginBalance=totalMarginBalance, \
                           availableBalance=availableBalance, \
                           maxWithdrawAmount=maxWithdrawAmount)
    db.session.add(account)
    db.session.commit()
    pass  


def update_account(account_data, active_api_label):
    totalWalletBalance, totalUnrealizedProfit, totalMarginBalance, availableBalance, maxWithdrawAmount = account_data
    account = AccountModel.query.filter_by(api_label=active_api_label, user_id=current_user.id).first()
    if account != None:
        account.totalWalletBalance, account.totalUnrealizedProfit, account.totalMarginBalance, account.availableBalance, account.maxWithdrawAmount = totalWalletBalance, totalUnrealizedProfit, totalMarginBalance, availableBalance, maxWithdrawAmount
        db.session.commit()   
    pass


def select_account(active_api_label):
    account = AccountModel.query.filter_by(api_label=active_api_label, user_id=current_user.id).first()
    return account


# orders interactions
def delete_all_orders(active_api_label):
    orders = OrdersModel.query.filter_by(api_label=active_api_label, user_id=current_user.id).all()
    if len(orders) > 0:
        for order in orders:
            db.session.delete(order)
    db.session.commit()
    pass 


def create_order(order_data, active_api_label):
    origQty, price, side, positionSide, status, symbol, time, ord_type = order_data
    order = OrdersModel(api_label=active_api_label, \
                        user_id=current_user.id, \
                        origQty=origQty, price=price, \
                        side=side, \
                        positionSide=positionSide, \
                        status=status, \
                        symbol=symbol, \
                        time=time, \
                        type=ord_type)
    db.session.add(order)
    pass 


def scrape(active_api_label, app):
    try:
        _scrape(active_api_label, app)
    except HTTPRequestError as exc:
        if app is None:
            print(exc)
        else:
            app.logger.error(str(exc))


def _scrape(active_api_label, app):
    global LAST_SCRAPE_TIME
    global LAST_SCRAPE_TIME_SEC
    start = time.time()
    if start - LAST_SCRAPE_TIME_SEC < MIN_SCRAPE_PERIOD_SEC:
        return 
    LAST_SCRAPE_TIME_SEC = start
    db_setup()

    up_to_date = False
    weightused = 0
    processed, updated_positions, new_positions, updated_orders = 0, 0, 0, 0
    sleeps = 0

    if weightused < 1000:
        responseHeader, responseJSON = send_signed_request(active_api_label, "GET", "/fapi/v1/openOrders")
        weightused = int(responseHeader["X-MBX-USED-WEIGHT-1M"])
        delete_all_orders(active_api_label)
        for order in responseJSON:
            updated_orders += 1
            row = (
                float(order["origQty"]),
                float(order["price"]),
                order["side"],
                order["positionSide"],
                order["status"],
                order["symbol"],
                int(order["time"]),
                order["type"],
            )
            create_order(row, active_api_label)

    responseHeader, responseJSON = send_signed_request(active_api_label, "GET", "/fapi/v2/account")
    weightused = int(responseHeader["X-MBX-USED-WEIGHT-1M"])

    overweight = False
    try:
        positions = responseJSON["positions"]
    except Exception:
        print("overweight!!!!!")
        overweight = True

    if not overweight:
        totals_row = (
            float(responseJSON["totalWalletBalance"]),
            float(responseJSON["totalUnrealizedProfit"]),
            float(responseJSON["totalMarginBalance"]),
            float(responseJSON["availableBalance"]),
            float(responseJSON["maxWithdrawAmount"]),
        )
        accountCheck = select_account(active_api_label)
        if accountCheck is None:
            create_account(totals_row, active_api_label)
        elif float(accountCheck.totalWalletBalance) != float(responseJSON["totalWalletBalance"]):
            update_account(totals_row, active_api_label)
        delete_all_positions(active_api_label)
        positions = [*filter(lambda x: float(x["positionAmt"]) != 0, positions)]
        for position in positions:
            position_row = (
                float(position["unrealizedProfit"]),
                int(position["leverage"]),
                float(position["entryPrice"]),
                float(position["positionAmt"]),
                position["symbol"],
                position["positionSide"],
            )
            position_check = select_position(position["symbol"], position["positionSide"], active_api_label)
            if position_check is None:
                create_position(position_row, active_api_label)
                new_positions += 1
                
            elif float(position_check.unrealizedProfit) != float(position["unrealizedProfit"]):
                update_position(position_row, active_api_label)
                updated_positions += 1

    while not up_to_date:
        if weightused > 1100:
            print(f"Weight used: {weightused}\nProcessed: {processed}\n skipping for next time ")
            break

        income_check = select_latest_income(active_api_label)
        if income_check is None:
            one_month_ago = get_one_mounth_ago()
            startTime = int(
                one_month_ago.timestamp() * 1000
            )
        else:
            startTime = income_check.time
        params = {"startTime": startTime + 1, "limit": 1000}

        responseHeader, responseJSON = send_signed_request(active_api_label, "GET", "/fapi/v1/income", params)
        weightused = int(responseHeader["X-MBX-USED-WEIGHT-1M"])

        if len(responseJSON) == 0:
            up_to_date = True
        else:
            for income in responseJSON:
                if len(income["tradeId"]) == 0:
                    income["tradeId"] = 0
                income_row = (
                    int(income["tranId"]),
                    income["symbol"],
                    income["incomeType"],
                    income["income"],
                    income["asset"],
                    income["info"],
                    int(income["time"]),
                    int(income["tradeId"]),
                )
                create_income(income_row, active_api_label)
                processed += 1

    elapsed = time.time() - start
    db.session.commit()
    if app is not None:
        current_app.logger.info(
            "Orders updated: %s; Positions updated: %s (new: %s); Trades processed: %s; Time elapsed: %s; Sleeps: %s",
            updated_orders,
            updated_positions,
            new_positions,
            processed,
            timedelta(seconds=elapsed),
            sleeps,
        )
    else:
        print(
            "Orders updated: {}\nPositions updated: {} (new: {})\nTrades processed: {}\nTime elapsed: {}\nSleeps: {}".format(
                updated_orders,
                updated_positions,
                new_positions,
                processed,
                timedelta(seconds=elapsed),
                sleeps,
            )
        )

def get_liquidation_price(active_api_label, coin) -> typing.Dict:
    data = {"SHORT": 0, "LONG": 0}
    params = {"symbol": coin}
    _, json_response = send_signed_request(active_api_label, "GET", "/fapi/v2/positionRisk", params)
    if isinstance(json_response, list) and len(json_response) != 0 and json_response is not None:
        for response in json_response:
            if "positionSide" not in response:
                continue
            if "liquidationPrice" not in response:
                continue
            
            if response["positionSide"] == "SHORT":
                data["SHORT"] += decimals.create_decimal(response["liquidationPrice"])
            elif response["positionSide"] == "LONG":
                data["LONG"] += decimals.create_decimal(response["liquidationPrice"])
    return data
