import c_achievements
import c_user
from typing import Any


HEHET_COLLECTED = "hehet_collected"
HEHET_SPENT = "hehet_spent"
CARDS_COLLECTED = "cards_collected"

achievement_names = {
    HEHET_COLLECTED: {
        "name": "Hehet Collected"
    },
    HEHET_SPENT: {
        "name": "Hehet Spent"
    },
    CARDS_COLLECTED: {
        "name": "Cards Collected"
    }
}

achievement_goals = {
    HEHET_COLLECTED: {
        100_000: [],
        1_000_000: [],
        10_000_000: []
    },
    HEHET_SPENT: {
        100_000: [],
        1_000_000: [],
        10_000_000: []
    },
    CARDS_COLLECTED: {
        100: [],
        1_000: [],
        10_000: []
    }
}


def find_first(achievements: list[c_achievements.Achievement], name: str) -> c_achievements.Achievement:
    for achievement in achievements:
        if achievement.name.lower() == name.lower():
            return  achievement


def get_progress_from_achievements(user: c_user.User, achievement: str):
    achievement_ = find_first(user.achievements.achievements, achievement)
    info = achievement_goals[achievement]
    milestones = list(info.keys())
    rewards = list(info.values())

    milestone = milestones[min(len(milestones), achievement_.collected)]
    return f"{achievement_.progress:,} / {milestone:,}"



check_progress = {
    HEHET_COLLECTED: (lambda user, achievement: get_progress_from_achievements(user, achievement)),
    HEHET_SPENT: (lambda user, achievement: get_progress_from_achievements(user, achievement)),
    CARDS_COLLECTED: (lambda user, achievement: get_progress_from_achievements(user, achievement))
}


async def get_achievement_progress(user: c_user.User, index_range: tuple[int, int] | list[int, int]):
    selected_achievements = list(achievement_names.keys())[index_range[0]: min(len(achievement_names), index_range[1])]

    info = []
    for achievement in selected_achievements:
        progress = check_progress[achievement](user, achievement)
        info.append([achievement, progress])

    return info


async def add_to_progress(db: Any, user_id: int, achievement: str, amount: int) -> None:
    achievement_progress = await db.get_achievement(user_id, achievement)
    await db.update_achievement(
        user_id = user_id,
        achievement = achievement,
        new_data = {
            "progress": achievement_progress.progress + amount
        }
    )

