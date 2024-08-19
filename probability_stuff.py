import random


def find_rarity(rarity: str, cards: list[str]):
    rarity = rarity.upper()
    for card in cards:
        if rarity == card[0].upper():
            return card.upper()


def get_random_card(chances: dict[str, float], cards: list[str]) -> str:
    rarities = {card[0].upper() for card in cards}
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
