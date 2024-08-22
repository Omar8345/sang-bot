import os
import c_card
import c_user
from typing import Any
import card_info


CARD_DIRECTORY = card_info.CARD_DIRECTORY

cards = []

CHANCES = { # out of 100
    "E": 30,
    "D": 25,
    "C": 20,
    "B": 15,
    "A": 10
}

EVENT_CHANCES = { # out of 100
    "E": 42,
    "D": 20,
    "C": 15,
    "B": 10,
    "A": 8,
    "S": 5
}

LIMITED_EVENT_CHANCES = { # out of 100
    "E": 42,
    "D": 20,
    "C": 15,
    "B": 10,
    "A": 7,
    "S": 4,
    "SSR": 2
}

def get_chances():
    return CHANCES


def find_card(user: c_user.User, card: str) -> c_card.Card | None:
    for owned_card in user.cards:
        if card.lower() == owned_card.card_id.lower():
            return owned_card

    return None


def add_cards(user: c_user.User, card: str, amount: int = 1) -> None:
    user.cards.append({
        "user_id": user.user_id,
        "card_id": card
    })


def count_cards(user: c_user.User) -> int:
    amount = 0
    for card in user.cards:
        amount += card.amount

    return amount


def load_card_info():
    ...


def get_card_image_from_id(card_id: str) -> str:
    info = card_info.card_info[card_id.upper()]
    return os.path.join(CARD_DIRECTORY, info.group, info.era, f"{card_id.upper()}.png")
