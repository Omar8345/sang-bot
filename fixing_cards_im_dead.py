import card_info
import os
import json

# for card in os.listdir("cards"):
#     if card.endswith(".png"):
#         card_id = card.split(".")[0]
#         try:
#             os.rename(f"cards/{card}", f"cards/{card_info.card_info[card_id].group}/{card_info.card_info[card_id].era}/{card}")
#         except Exception as e:
#             print(e)

CARD_DIRECTORY = "cards"

for group in os.listdir(CARD_DIRECTORY):

    group_path = os.path.join(CARD_DIRECTORY, group)

    if not os.path.isdir(group_path): continue
    for era in os.listdir(group_path):
        era_path = os.path.join(group_path, era)

        info = {}
        for card in os.listdir(era_path):
            if not card.endswith(".png"):
                continue

            card_id = card.split('.')[0]
            info[card_id.upper()] = {
                "name": card_info.card_info[card_id].name,
                "rarity": card_id[0].upper(),
            }


        with open(os.path.join(era_path, "_cards_info.json"), "w") as f:
            json.dump(info, f, indent = 2)

