import json

with open("permissions.json") as f:
    permissions = json.load(f)

    all_permissions = permissions["all_permissions"]
    admins = permissions["admins"]
    admin_permissions = permissions["admin_permissions"]
    extra_permissions = permissions["extra_permissions"]


def has_permissions(user_id: int, command: str) -> bool:
    if user_id in all_permissions:
        return True

    if user_id in admins:
        return command in admin_permissions

    if user_id in extra_permissions:
        return command in extra_permissions[user_id]
