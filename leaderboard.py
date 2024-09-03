import json
import math
import os
import c_user
import card_info
import db
from typing import Iterable, Any, Callable
from bot import bot


LEADERBOARDS_DIRECTORY = "leaderboards"

def load_top_hehet():
    with open(os.path.join(LEADERBOARDS_DIRECTORY, "top_hehet.json")) as f:
        return json.load(f)


def load_top_cards():
    with open(os.path.join(LEADERBOARDS_DIRECTORY, "top_cards.json")) as f:
        return json.load(f)

def load_top_idol(name: str) -> list[list[int]]:
    path = os.path.join(LEADERBOARDS_DIRECTORY, f"idol_{name}.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def load_top_group(group: str) -> list[list[int]]:
    path = os.path.join(LEADERBOARDS_DIRECTORY, f"group_{group.lower()}.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def add_sorted(
        _list: Iterable,
        item: Any,
        compare: Callable = lambda a, b: a > b,
        limit: int = math.inf
    ):
    count = 0
    for i, v in enumerate(_list):
        if compare(item, v):
            _list.insert(i, item)
            if len(_list) > limit:
                del _list[-1]
            return

        if count >= limit:
            while len(_list) > limit:
                del _list[-1]

            break
        count += 1

    if len(_list) < limit:
        _list.append(item)


async def calculate_hehet_leaderboard():
    user_hehets = []
    for user in await db.db.user.find_many():
        discord_user = bot.get_user(user.user_id)
        if discord_user is None or discord_user.bot:
            continue

        add_sorted(
            user_hehets,
            [user.balance, user.user_id],
            lambda a, b: a[0] > b[0],
            10
        )

    with open(os.path.join(LEADERBOARDS_DIRECTORY, "top_hehet.json"), "w") as f:
        json.dump(user_hehets, f, indent = 2)


def get_group_count(group):
    async def not_a_wrapper_idk_what_this_is(user: c_user.User):
        amount = 0
        for card in user.cards:
            if card.card_id not in card_info.card_info: continue

            if card_info.card_info[card.card_id].group.lower() == group.lower():
                amount += card.amount

        return amount

    return not_a_wrapper_idk_what_this_is


def get_idol_count(idol):
    async def not_a_wrapper_idk_what_this_is(user: c_user.User):

        amount = 0
        for card in user.cards:
            if card.card_id not in card_info.card_info: continue
            if card_info.card_info[card.card_id].name.lower() == idol.lower():
                amount += card.amount

        return amount

    return not_a_wrapper_idk_what_this_is

async def calculate_cards_leaderboard():
    user_cards = []

    for user in await db.db.user.find_many():
        discord_user = bot.get_user(user.user_id)
        if discord_user is None or discord_user.bot:
            continue

        card_count = await db.get_card_count(user_id = user.user_id)
        add_sorted(
            user_cards,
            [card_count, user.user_id],
            lambda a, b: a[0] > b[0],
            10
        )

    with open(os.path.join(LEADERBOARDS_DIRECTORY, "top_cards.json"), "w") as f:
        json.dump(user_cards, f, indent = 2)

    for group in card_info.card_groups_enum:
        await generate_leaderboard_based_on_every_user(
            criteria = get_group_count(group.name),
            name = f"group_{group.name}"
        )

    for idol in card_info.idols_enum:
        await generate_leaderboard_based_on_every_user(
            criteria = get_idol_count(idol),
            name = f"idol_{idol}"
        )


async def generate_leaderboard_based_on_every_user(
        criteria: Callable,
        name: str
):
    user_stats = []

    for user in await db.db.user.find_many(
        include = {
            "cards": True
        }
    ):
        discord_user = bot.get_user(user.user_id)
        if discord_user is None or discord_user.bot:
            continue

        card_count = await criteria(user)
        add_sorted(
            user_stats,
            [card_count, user.user_id],
            lambda a, b: a[0] > b[0],
            10
        )

    with open(os.path.join(LEADERBOARDS_DIRECTORY, f"{name.lower()}.json"), "w") as f:
        json.dump(user_stats, f, indent = 2)


async def calculate_leaderboards():
    await calculate_cards_leaderboard()
    await calculate_hehet_leaderboard()
