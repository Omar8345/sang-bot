import random
import time
import discord
from typing import Literal
import c_card
import card_info
import group_cards
from bot import tree
from settings import settings
import db
import card_manager
from enum import Enum
from io import BytesIO
import probability_stuff
from discord import ButtonStyle
from discord.ui import View, Button
import json


DROP_COOLDOWN_SECONDS = 120

# IDs
HEHET = 0
REGULAR_CARD = 1
FEATURED_CARD = 2
CARD = 3
BUDS = 4

CHANCES = { # out of 100
    HEHET: 25,
    REGULAR_CARD: 60,
    BUDS: 10,
    FEATURED_CARD: 5
}

gacha_types = Literal["Standard Gacha"]
gacha_groups = Enum("GachaNames", {name: card_info.group_info[name] for name in card_info.group_list})


@tree.command(name="gacha", description="get random rewards, including exclusive cards", guild=discord.Object(id = settings.guild_id))
async def gacha(interaction: discord.Interaction, gacha_name: gacha_types, group: gacha_groups, amount: int | None = 1):
    user_id = interaction.user.id
    user = await db.get_user(
        user_id
    )

    if user.buds < amount:
        await interaction.response.send_message(f"You don't have this many buds")
        return

    if amount <= 0:
        await interaction.response.send_message(f"Amount must be bigger than 0")
        return

    if amount > 10:
        await interaction.response.send_message(f"Amount can't be larger than 10")
        return

    gacha_info = await db.get_gacha_info(user_id)

    pity = gacha_info.pity
    rewards = []
    for _ in range(amount):
        pity -= 1
        if pity <= 0 and gacha_info.selected_card != "none":
            rewards.append([
                CARD,
                gacha_info.selected_card
            ])
            pity = random.randint(50, 100)
            continue
        else:
            drop_type = probability_stuff.get_random_from(CHANCES)

        cards_from_group = card_info.group_info[group.name]
        if drop_type == HEHET:
            rewards.append([group_cards.HEHET_ID, random.randint(5_000, 10_000)])
        elif drop_type == BUDS:
            rewards.append([group_cards.BUD_ID, random.randint(1, 2)])
        elif drop_type == REGULAR_CARD:
            rewards.append([CARD, probability_stuff.get_random_card(card_manager.get_chances(), cards_from_group)])
        elif drop_type == FEATURED_CARD:
            _cards = card_info.gacha_only_cards
            if gacha_info.selected_card != "none":
                _cards += [gacha_info.selected_card] * 3

            rewards.append([CARD, random.choice(_cards)])

    cards = [reward[1] for reward in rewards if reward[0] == CARD]
    hehet = sum([reward[1] for reward in rewards if reward[0] == group_cards.HEHET_ID])
    buds = sum([reward[1] for reward in rewards if reward[0] == group_cards.BUD_ID])


    embed = discord.Embed(
        title = "Gacha Results",
        color = settings.embed_color
    )


    await db.update_user(
        user_id,
        new_data = {
            "balance": user.balance + hehet,
            "buds": user.buds + buds
        }
    )

    await db.update_gacha_info(
        user_id,
        new_data = {
            "pity": pity
        }
    )

    cards = [i[1] for i in rewards if i[0] not in [group_cards.BUD_ID, group_cards.HEHET_ID]]
    cards_count = dict.fromkeys(
        cards,
        0
    )

    for card in cards:
        cards_count[card] += 1

    for card, amount in cards_count.items():
        await db.add_cards(
            user_id,
            c_card.Card(
                user_id = user_id,
                card_id = card
            ),
            amount
        )

    await interaction.response.defer()

    cards_image = BytesIO()
    group_cards.generate_image(
        rewards,
        cards_image,
        text = True,
        list_items = True
    )

    cards_image.seek(0)
    file = discord.File(cards_image, filename="img.png")

    embed.set_image(url="attachment://img.png")

    await db.create_gacha_history(
        user_id,
        rewards = str(rewards)
    )

    await interaction.followup.send(file=file, embed=embed)


# old function, please ignore
async def __gacha_hehet(interaction: discord.Interaction):
    amount = random.randint(5_000, 10_000)
    embed = discord.Embed(
        title = "Gacha",
        color = settings.embed_color,
        description = f"+ `{amount:,}` {settings.hehet_emoji}"
    )

    user = await db.get_user(interaction.user.id)
    await db.update_user(
        user_id = interaction.user.id,
        new_data = {
            "balance": user.balance + amount
        }
    )

    await interaction.response.send_message(embed=embed)


@tree.command(name="gacha_history", description="see you gacha pull history", guild=discord.Object(id = settings.guild_id))
async def gacha_history(interaction: discord.Interaction, page: int = 1):
    user_id = interaction.user.id
    user = await db.get_gacha_info(
        user_id,
        include = {
            "gacha_history": True
        }
    )

    await show_gacha_history(interaction, page - 1)


async def show_gacha_history(interaction: discord.Interaction, index: int = 0, edit: bool = False):
    user_id = interaction.user.id

    gacha_info = await db.get_gacha_info(
        user_id,
        include = {
            "gacha_history": True
        }
    )

    gacha_history = [[i.id, i] for i in gacha_info.gacha_history]
    gacha_history.sort(key = (lambda x: x[0]), reverse=True)

    if index >= len(gacha_history) or index < 0:
        if edit:
            await interaction.response.defer()
        else:
            await interaction.response.send_message(f"Invalid page number (must be from 1 to {len(gacha_history)})")
        return

    _id, history = gacha_history[index]
    embed = discord.Embed(
        title = f"Gacha History - <t:{history.time}:R>",
        colour = settings.embed_color
    )

    rewards = json.loads(history.rewards.replace("'", '"'))
    await interaction.response.defer()

    cards_image = BytesIO()
    group_cards.generate_image(
        rewards,
        cards_image,
        text = True,
        list_items = True
    )

    cards_image.seek(0)
    file = discord.File(cards_image, filename="img.png")

    embed.set_image(url="attachment://img.png")


    view = View(timeout=60)
    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = "<",
            custom_id = f"[{user_id}]gacha_history%{index}%back",
            disabled = (index == 0)
        )
    )

    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = f"{index + 1} / {len(gacha_history)}",
            disabled = True
        )
    )

    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = ">",
            custom_id = f"[{user_id}]gacha_history%{index}%next",
            disabled = (index == len(gacha_history) - 1)
        )
    )

    if edit:
        await interaction.message.edit(content="", attachments = [file], embed = embed, view = view)
    else:
        await interaction.followup.send(file = file, embed = embed, view = view)


@tree.command(name="gacha_set", description="pick a gacha only card to increase your chances of getting it", guild=discord.Object(id = settings.guild_id))
async def gacha_set(interaction: discord.Interaction, name: str):
    name = name.upper()
    user_id = interaction.user.id

    if name not in card_info.gacha_only_cards:
        await interaction.response.send_message(
            f"`{name}` is not a gacha only card, choose one of these:\n{', '.join([f'`{i}`' for i in card_info.gacha_only_cards])}"
        )
        return

    await db.update_gacha_info(
        user_id,
        new_data = {
            "selected_card": name
        }
    )

    await interaction.response.send_message(f"Increased chances for `{name}` in gacha pulls")
