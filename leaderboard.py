import json
import math
import db
from typing import Iterable, Any, Callable
from bot import bot


def load_top_hehet():
    with open("top_hehet.json") as f:
        return json.load(f)


def load_top_cards():
    with open("top_cards.json") as f:
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

    with open("top_hehet.json", "w") as f:
        json.dump(user_hehets, f, indent = 2)


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

    with open("top_cards.json", "w") as f:
        json.dump(user_cards, f, indent = 2)

async def calculate_leaderboards():
    await calculate_cards_leaderboard()
    await calculate_hehet_leaderboard()