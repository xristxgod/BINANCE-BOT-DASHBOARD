import typing

from addition.db_wallet import get_users_id

class FavoritesUsers:

    def __init__(self):
        self.favorites_users: typing.List = []

    def change_to_favorites(self, user_id: int) -> str:
        for index, user in enumerate(self.favorites_users):
            if user == user_id:
                del self.favorites_users[index]
                return "del"
        else:
            self.favorites_users.append(user_id)
            return "add"

    def select_all_users(self) -> bool:
        try:
            self.favorites_users = get_users_id()
            return True
        except Exception as error:
            return False

    def is_in_favorites(self, user_id: int) -> bool:
        for user in self.favorites_users:
            if user == user_id:
                return True
        else:
            return False

    @property
    def get_user_favorite(self) -> typing.List[int]:
        return self.favorites_users

    def clear_favorites_users(self) -> None:
        self.favorites_users = []

