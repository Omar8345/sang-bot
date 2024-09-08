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


@tree.command(name="view", description="view a card from your inventory", guild=discord.Object(id = settings.guild_id))
async def search(interaction: discord.Interaction, card: str):
    card = card.upper()
    if card not in card_info.card_info:
        await interaction.response.send_message("Card not found, or it doesn't have any information")
        return

    card_information = card_info.card_info[card]
    rarity = card_info.card_info[card.upper()].rarity

    user = await db.get_user(
        user_id = interaction.user.id,
        include = {
            "cards": True
        }
    )

    card_owned = card_manager.find_card(user, card)
    if card_owned is None:
        await interaction.response.send_message("You don't own this card")
        return
    else:
        cards_owned = card_owned.amount

    embed = discord.Embed(
        title = f"View",
        description = \
            f"ID: {card}\n"
            f"Idol: {card_info.card_info[card].name}\n"
            f"Group: {card_information.group}\n"
            f"Era: {card_information.era}\n"
            f"Rarity: {settings.tier_emojis[rarity]}\n"
            f"Copies owned: {cards_owned:,}",
        colour=settings.embed_color,
    )

    await interaction.response.defer()

    file = discord.File(card_manager.get_card_image_from_id(card), filename=f"{card}.png")
    embed.set_image(url=f"attachment://{card}.png")

    await interaction.followup.send(file=file, embed=embed)
