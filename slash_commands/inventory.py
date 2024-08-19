import discord
import c_card
import card_info
from bot import tree
from settings import settings
import os
import db
import slash_commands.drop as drop
import card_manager
from functools import reduce
from discord.ui import View, Button
from discord import ButtonStyle
import math


CARDS_PER_PAGE = 8

def hash_card(card: c_card.Card) -> int:
    return reduce(lambda a, b: a << 5 | (ord(b) - ord("a")), card.card_id.lower(), 0)

rank_order = {
    "S": 0,
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6
}

@tree.command(name="inventory", description="view your cards", guild=discord.Object(id = settings.guild_id))
async def inventory(interaction: discord.Interaction): # old method: ', card: str | None = None):'
    await show_inventory(interaction)


async def show_inventory(interaction: discord.Interaction, page: int = 1, edit: bool = False):
    page -= 1
    if page < 0:
        return
    user_id = interaction.user.id
    user_data = await db.get_user(
        user_id,
        include = {
            "cards": True
        }
    )

    embed = discord.Embed(
        title = "Inventory",
        color = settings.embed_color
    )

    user_data.cards.sort(
        key = (lambda x: rank_order[x.card_id[0].upper()])
    )

    for card in user_data.cards[page * CARDS_PER_PAGE: min(len(user_data.cards), (page + 1) * CARDS_PER_PAGE)]:
        tier = card.card_id[0].upper()
        info = card_info.card_info[card.card_id.upper()]
        name, group, era = info.name, info.group, info.era

        embed.add_field(
            value = f"{card.amount:,}x {settings.tier_emojis[tier]} **{group}** __{era}__ {name} `{card.card_id.upper()}`",
            name = "",
            inline = False
        )

    view = View(timeout=60)
    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = "<",
            custom_id = f"[{user_id}]inventory%{page + 1}%back",
            disabled = (page == 0)
        )
    )

    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = f"{page + 1} / {math.ceil(len(user_data.cards) / CARDS_PER_PAGE)}",
            disabled = True
        )
    )

    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = ">",
            custom_id = f"[{user_id}]inventory%{page + 1}%next",
            disabled = (page + 1 == math.ceil((len(user_data.cards) / CARDS_PER_PAGE)))
        )
    )

    if edit:
        await interaction.response.defer()
        await interaction.message.edit(embed = embed, view = view)
    else:
        await interaction.response.send_message(embed = embed, view = view)

# old method, please ignore
async def show_inventory_slot(interaction: discord.Interaction, index: int = 0, edit: bool = False):
    user_id = interaction.user.id

    user = await db.get_user(
        user_id,
        include = {
            "cards": True
        }
    )

    embed = discord.Embed(
        title = f"Inventory - `{len(user.cards):,}` different cards",
        colour = settings.embed_color
    )

    cards: list[c_card.Card] = list(zip([hash_card(card) for card in user.cards], user.cards))

    if index >= len(cards) or index < 0:
        await interaction.response.defer()
        return

    cards.sort(key=lambda x: x[0])
    card = cards[index][1]
    card_id = card.card_id

    embed.description = f"You have `{card.amount:,}` of this card (`{card_id}`)"

    await interaction.response.defer()
    file = discord.File(os.path.join(drop.CARD_DIRECTORY, f"{card_id}.png"), f"{card_id}.png")
    embed.set_image(url=f"attachment://{card_id}.png")

    view = View(timeout=60)
    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = "<",
            custom_id = f"[{user_id}]inventory{index}back",
            disabled = (index == 0)
        )
    )

    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = f"{index + 1} / {len(cards)}",
            disabled = True
        )
    )

    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = ">",
            custom_id = f"[{user_id}]inventory{index}next",
            disabled = (index == len(cards) - 1)
        )
    )

    if edit:
        await interaction.message.edit(content="", attachments = [file], embed = embed, view = view)
    else:
        await interaction.followup.send(file = file, embed = embed, view = view)


async def show_card(interaction: discord.Interaction, card: c_card.Card):
    card_id = card.card_id

    embed = discord.Embed(
        title=f"Card `{card_id}`",
        colour=settings.embed_color,
        description=f"You have {card.amount:,} of this card"
    )


    await interaction.response.defer()
    file = discord.File(os.path.join(drop.CARD_DIRECTORY, f"{card_id}.png"), f"{card_id}.png")
    embed.set_image(url=f"attachment://{card_id}.png")

    await interaction.followup.send(file=file, embed=embed)
