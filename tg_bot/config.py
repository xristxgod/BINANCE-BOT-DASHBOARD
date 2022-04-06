import os
import decimal
import logging

decimals = decimal.Context()
decimals.prec = 8

TOKEN = os.getenv("TOKEN", "5283221517:AAGx3HIayIo9kKpaHlQlM85TCZyygqr5fq8")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "xrist88b@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "mamedov00")
API_URL = os.getenv("API_URL", "http://192.168.0.193/")

logger = logging.getLogger(__name__)