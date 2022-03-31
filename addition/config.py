import os
import decimal
import logging
import emoji
from decouple import config

from hlp import BASE_DIR, BASE_FILE, ROOT_DIR

logger = logging.getLogger(__name__)

_node_url = config("TRON_NODE", "http://3.225.171.164:8090")
_network = config("TRON_NETWORK", "shasta")

decimals = decimal.Context()
decimals.prec = 8

percentage_of_pnl = int(config("PERCENTAGE_OF_WITHDRAWALS_PER_DAY", "30"))
db_path = config("DB_URL", os.path.join(BASE_DIR, "database.db"))

adminWallet = {
    "address": config("ADMIN_ADDRESS", ""),
    "privateKey": config("ADMIN_PRIVATE_KEY", "")
}
LIMIT_USDT = decimals.create_decimal(config("LIMIT_USDT", "2.0"))
ADMIN_TOKEN = config("ADMIN_TOKEN", "")
ADMIN_IDS = config("ADMIN_IDS", ",").split(",")

USER_TOKEN = config("USER_TOKEN", "")


if _network == "mainnet":    __token = "tokensMainNet.json"
else:   __token = "tokensShastaNet.json"
# File for TRC20 tokens
fileTokens = os.path.join(BASE_FILE, __token)

symbol = {
    "add": emoji.emojize(":green_circle:"),
    "dec": emoji.emojize(":red_circle:")
}

PDF_INSTRUCTIONS = os.path.join(BASE_FILE, "instructions.pdf")