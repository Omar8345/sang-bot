import c_user

achievements = [
    ""
]

async def get_achievement_progress(user: c_user.User, index_range: tuple[int, int] | list[int, int]):
    selected_achievements = achievements[index_range[0]: min(len(achievements), index_range[1])]