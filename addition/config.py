import os
import decimal
import logging

from hlp import BASE_DIR

logger = logging.getLogger(__name__)

_node_url = "http://3.225.171.164:8090"
_network = "shasta"

decimals = decimal.Context()
decimals.prec = 8

percentage_of_pnl = 1
db_path = os.path.join(BASE_DIR, "database.db")

adminWallet = ""