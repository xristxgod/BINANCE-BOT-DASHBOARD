import os
import decimal
import logging
import emoji

decimals = decimal.Context()
decimals.prec = 8

TOKEN = os.getenv("TOKEN", "")
ADMIN_IDS = os.getenv("ADMIN_IDS", ",").split(",")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
API_URL = os.getenv("API_URL", "")

SYMBOLS = {
    "moneyBank": emoji.emojize(":money_bag:"),
    "whiteLargeSquare": emoji.emojize(":white_large_square:"),
    "creditCard": emoji.emojize(":credit_card:"),
    "email": emoji.emojize(":envelope_with_arrow:"),
    "unlock": emoji.emojize(":unlocked:"),
    "lock": emoji.emojize(":locked:"),
    "admin": emoji.emojize(":globe_with_meridians:"),
    "user": emoji.emojize(":bust_in_silhouette:"),
}

logger = logging.getLogger(__name__)