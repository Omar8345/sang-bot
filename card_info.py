import enum
import json
from pydantic import BaseModel
import settings

all_upper_case = ["DK"]
all_lower_case = []

class CardInfo(BaseModel):
    name: str
    group: str
    era: str


# dont edit this pliz
all_upper_case = [i.upper() for i in all_upper_case]
all_lower_case = [i.lower() for i in all_lower_case]

def add_card(id: str, name: str, era: str, group: str) -> None:
    with open("card_info.json") as f:
        text = settings.remove_comments(f.read(), '//')

    loaded = json.loads(text)
    with open("card_info.json", "w") as f:
        loaded["cards"][id] = {
            "group": group,
            "name": name,
            "era": era
        }
        json.dump(loaded, f, indent = 2)


def _capitalize_names(name: str) -> str:
    if name.upper() in all_upper_case:
        return name.upper()
    elif name.lower() in all_lower_case:
        return name.lower()
    else:
        return name.lower().title()


with open("card_info.json") as f:
    text = settings.remove_comments(f.read(), '//')
    loaded = json.loads(text)

    cards, gacha_only_cards = loaded["cards"], loaded["gacha_only_cards"]

    cards = {_id.upper(): {field: _capitalize_names(value) for field, value in data.items()} for _id, data in cards.items()}

    card_info: dict[str, CardInfo] = {card_id: CardInfo(**info) for card_id, info in cards.items()}
    non_gacha_cards_info: dict[str, CardInfo] = {card_id: CardInfo(**info) for card_id, info in cards.items() if card_id.upper() not in gacha_only_cards}

group_list = list({card.group for card in non_gacha_cards_info.values()})
group_info = {group: [] for group in group_list}

non_gacha_cards_id = [i for i in non_gacha_cards_info.keys()]

for card_id, card in non_gacha_cards_info.items():
    group_info[card.group].append(card_id)

card_groups_enum = enum.Enum(
    "CardGroups",
    {group: i for i, group in enumerate(list({card.group for card in card_info.values()}))}
)

idols_enum = enum.Enum(
    "IdolsEnum",
    {name: i for i, name in enumerate(list({card.name for card in card_info.values()}))}
)
