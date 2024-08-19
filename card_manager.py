import c_card
import c_user


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
