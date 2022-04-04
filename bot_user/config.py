import os
import decimal
import logging

decimals = decimal.Context()
decimals.prec = 8

TOKEN = os.getenv("TOKEN", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
API_URL = os.getenv("API_URL", "")

logger = logging.getLogger(__name__)