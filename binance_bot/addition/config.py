import os
import decimal
import logging
import emoji
from decouple import config

from hlp import BASE_DIR, BASE_FILE, BASE_STATIC

logger = logging.getLogger(__name__)

_node_url = config("TRON_NODE", "http://3.225.171.164:8090")
_network = config("TRON_NETWORK", "shasta")

decimals = decimal.Context()
decimals.prec = 8

percentage_of_pnl = int(config("PERCENTAGE_OF_WITHDRAWALS_PER_DAY", "30"))
db_path = os.path.join(BASE_DIR, "database.db")

adminWallet = {
    "address": config("ADMIN_ADDRESS"),
    "privateKey": config("ADMIN_PRIVATE_KEY")
}
LIMIT_USDT = decimals.create_decimal(config("LIMIT_USDT", "2.0"))

TOKEN = config("TOKEN")
ADMIN_IDS = config("ADMIN_IDS").split(",")


if _network == "mainnet":    __token = "tokensMainNet.json"
else:   __token = "tokensShastaNet.json"
# File for TRC20 tokens
fileTokens = os.path.join(BASE_FILE, __token)

symbol = {
    "add": emoji.emojize(":green_circle:"),
    "dec": emoji.emojize(":red_circle:")
}

SENDER_EMAIL = config("SENDER_EMAIL")
SENDER_PASSWORD = config("SENDER_PASSWORD")
# https://www.youtube.com/watch?v=zYWpEJAHvaI | 49:00 - Если проблемиы с отправкой сообщения
SENDER_SERVER = config("SENDER_SERVER", "smtp.gmail.com")

BOT_NAME = config("BOT_NAME")

USERS_FILE_PATH = os.path.join(BASE_FILE, "users_file.json")
USERS_TO_FAVORITES_FILE_PATH = os.path.join(BASE_FILE, "favorites.json")

PDF_FILE_PATH = os.path.join(BASE_STATIC, "MyBotSetupInstructions.pdf")
EXCEL_FILE_PATH = os.path.join(BASE_STATIC, "report.xlsx")