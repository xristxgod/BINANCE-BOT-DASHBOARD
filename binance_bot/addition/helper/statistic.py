import typing

from addition.db_wallet import get_users_info_by_users_ids
from addition.config import decimals

def get_users_statistic(ids: typing.List):
    return get_users_info_by_users_ids(users_ids=ids)