import enum
import json
from pydantic import BaseModel
import settings
import os
from functools import reduce


all_upper_case = ["DK", "BTS", "RM", "(G)I-DLE", "SS", "WWE", "TXT"]
all_lower_case = []

CARD_DIRECTORY = "cards"
gacha_groups = ["floral event"] # lowercase

class CardInfo(BaseModel):
    name: str
    group: str
    era: str
    rarity: str


# dont edit this pliz
all_upper_case = [i.upper() for i in all_upper_case]
all_lower_case = [i.lower() for i in all_lower_case]


def _capitalize_names(name: str) -> str:
    if name.upper() in all_upper_case:
        return name.upper()
    elif name.lower() in all_lower_case:
        return name.lower()
    else:
        return name.lower().title()


__cards = []
def load_cards():
    if len(__cards) != 0:
        return __cards

    for group in os.listdir(CARD_DIRECTORY):
        group_path = os.path.join(CARD_DIRECTORY, group)

        if not os.path.isdir(group_path): continue
        for era in os.listdir(group_path):
            era_path = os.path.join(group_path, era)
            if not os.path.isdir(era_path): continue

            for card in os.listdir(era_path):
                if not card.endswith(".png"):
                    continue

                card_id = card.split('.')[0]
                __cards.append(card_id)

    return __cards


all_cards = load_cards()
cards = {}
gacha_only_cards_by_group = {}
for group in os.listdir(CARD_DIRECTORY):
    group_path = os.path.join(CARD_DIRECTORY, group)

    if not os.path.isdir(group_path): continue
    for era in os.listdir(group_path):
        era_path = os.path.join(group_path, era)
        if not os.path.isdir(era_path): continue

        era_info_path = os.path.join(era_path, "_cards_info.json")
        with open(era_info_path) as f:
            era_info = json.load(f)

        era_info_backup = os.path.join(era_path, "_cards_info_backup.json")
        with open(era_info_backup, "w") as f:
            json.dump(era_info, f)

        for card in os.listdir(era_path):
            if not card.endswith(".png"):
                continue

            card_id = card.split('.')[0].upper()

            cards[card_id] = {
                **era_info[card_id],
                "group": group,
                "era": era
            }

            if group.lower() in gacha_groups:
                if era not in gacha_only_cards_by_group:
                    gacha_only_cards_by_group[era] = [card_id]
                else:
                    gacha_only_cards_by_group[era].append(card_id)

gacha_only_cards = reduce((lambda a, b: a + b), gacha_only_cards_by_group.values(), [])

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

card_era_enum = enum.Enum(
    "CardGroups",
    {era: i for i, era in enumerate(list({card.era for card in card_info.values()}))}
)

non_gacha_cards_enum = enum.Enum(
    "CardGroups",
    {group: i for i, group in enumerate(list({card.group for card in card_info.values()}))}
)

idols_enum = {card.name for card in card_info.values()}
