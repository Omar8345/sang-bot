import c_user


def get_user(user_id: int, createNewUser_ifNotFound: bool = false) -> dict | None:
    if user_id not in users:
        if createNewUser_ifNotFound:
            users[user_id] = user.new_user()
        else:
            return None

    return users[user_id]


def update_user(user_id: int, user_data: user.User):
    ...

