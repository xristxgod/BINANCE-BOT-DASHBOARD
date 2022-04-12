from addition.db_wallet import get_users, get_capital, get_pnl_all_time, get_unrealized_pnl_all_time
from addition.config import decimals

def get_report_for_all_time():
    return {
        "activeUsers": len(get_users()),
        "totalCapital": "%.8f" % decimals.create_decimal(get_capital()["totalCapital"]),
        "totalIncome": "%.8f" % decimals.create_decimal(get_pnl_all_time()["totalIncome"]),
        "totalUnrealizedPNL": "%.8f" % decimals.create_decimal(get_unrealized_pnl_all_time()["totalUnrealizedPNL"])
    }
