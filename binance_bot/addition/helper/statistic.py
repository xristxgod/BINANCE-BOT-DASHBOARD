import typing

from addition.db_wallet import get_users_info_by_ids_list

def get_users_statistic(ids: typing.List):
    users_info: typing.Dict = get_users_info_by_ids_list(ids=tuple(ids))
    users = users_info["userInfo"]
    for user in users_info["incomeInfo"]:
        for u in users:
            if user["user_id"] == u["id"]:
                try:
                    u["apisLabel"].append({
                        "apiLabel": user["api_label"],
                        "totalIncome": user["totalIncome"]
                    })
                except KeyError as error:
                    u["apisLabel"] = [{
                        "apiLabel": user["api_label"],
                        "totalIncome": user["totalIncome"]
                    }]
    return users