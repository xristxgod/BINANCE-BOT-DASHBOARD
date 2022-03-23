import decimal
import logging

logger = logging.getLogger(__name__)

_node_url = "http://3.225.171.164:8090"
_network = "shasta"

decimals = decimal.Context()
decimals.prec = 8

percentage_of_pnl = 1
db_path = "C:\\Users\\79381\Desktop\\binance-bot-dashboard\\binance-bot-dashboard\\DB\\database.db"

adminWallet = ""