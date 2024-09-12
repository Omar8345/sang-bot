import random

import card_info
import card_manager


def get_chances():
    return card_manager.CHANCES


def get_random_from(chances: dict) -> str:
    rarities = list(chances.keys())
    random.shuffle(rarities)

    count = 0
    number = random.random() * 100
    for rarity in rarities:
        count += chances[rarity]
        if count >= number:
            return rarity


def find_rarity(rarity: str, cards: list[str]):
    rarity = rarity.upper()
    for card in cards:
        if rarity == card_info.card_info[card.upper()].rarity:
            return card.upper()

very_rare_thingies = ["S", "SS", "UR", "SSR"]
def get_random_card(chances: dict[str, float], cards: list[str], with_very_rare_thingies: bool = False) -> str:
    rarities = {card_info.card_info[card.upper()].rarity for card in cards}
    for i in very_rare_thingies:
        if i in rarities:
            rarities.remove(i)

    chances = {rarity: chance for rarity, chance in chances.items() if rarity in rarities}
    limit = sum(chances.values())

    number = random.uniform(0, limit)

    rarities = list(rarities)
    random.shuffle(rarities)

    cards = cards.copy()
    random.shuffle(cards)

    count = 0
    for rarity in rarities:
        count += chances[rarity]
        if count >= number:
            return find_rarity(rarity, cards)
