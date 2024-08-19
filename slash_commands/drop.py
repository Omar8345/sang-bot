import random
import time
import discord
import card_info
import c_card
import probability_stuff
from bot import tree
from settings import settings
import db
import os
import card_manager
from typing import Any


CARD_DIRECTORY = "cards"

DROP_COOLDOWN_SECONDS = 120

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


def load_cards():
    cards = [
        # removes file extension
        i.split('.')[0] \
        for i in os.listdir(CARD_DIRECTORY)
    ]
    return cards


# outdated
def __get_random_card(rarity: str) -> str | None:
    cards = load_cards()
    random.shuffle(cards)

    for card in cards:
        if card.lower().startswith(rarity.lower()):
            return card

    return None


def get_chances():
    return CHANCES


def get_random_from(chances: dict) -> Any:
    rarities = list(chances.keys())
    random.shuffle(rarities)

    count = 0
    number = random.random() * 100
    for rarity in rarities:
        count += chances[rarity]
        if count >= number:
            return rarity


# outdated
def __get_random_rarity():
    chances = get_chances()

    return get_random_from(chances)


@tree.command(name="drop", description="get a random card", guild=discord.Object(id = settings.guild_id))
async def drop(interaction: discord.Interaction):
    user_id = interaction.user.id
    cool_downs = await db.get_cooldown(user_id)

    if time.time() - cool_downs.drop > DROP_COOLDOWN_SECONDS: # cooldown expired
        user = await db.get_user(user_id, include = { "cards" : True })

        await db.update_cooldown(user_id, {"drop": int(time.time())})

        chances = get_chances()
        card = probability_stuff.get_random_card(chances, card_info.non_gacha_cards_id).upper()
        rarity = card[0]

        if card is not None:
            await db.add_cards(
                user_id = user_id,
                card = c_card.Card(
                    user_id = user_id,
                    card_id = card
                )
            )
            card_obj = card_manager.find_card(user, card)
            if card_obj is None:
                amount = 1
            else:
                amount = card_obj.amount + 1

            card_information = card_info.card_info[card]
            chances = get_chances()
            embed = discord.Embed(
                title = f"{settings.tier_emojis[rarity]} Tier {card_information.name} Card",
                description = \
                    f"This card has a *{chances[rarity]}%* chance of dropping!\n" + \
                    f"You can view this card under the group `{card_information.group}`, Era `{card_information.era}`, or the code `{card}`\n\n" + \
                    f"Obtained <t:{int(time.time())}:R>",
                colour=settings.embed_color,
            )
            if amount == 1:
                embed.set_footer(text = "You obtained this card")
            else:
                embed.set_footer(text = f"You have {amount:,} of this card")

            await interaction.response.defer()

            file = discord.File(os.path.join(CARD_DIRECTORY, f"{card}.png"), filename=f"{card}.png")
            embed.set_image(url=f"attachment://{card}.png")

            await interaction.followup.send(file=file, embed=embed)
        else:
            await  interaction.response.send_message(f"Rolled {rarity}")
    else:
        next_time = cool_downs.drop + DROP_COOLDOWN_SECONDS
        await interaction.response.send_message(f"You can only get a drop once ever 2 minutes! Try again <t:{next_time}:R>")
