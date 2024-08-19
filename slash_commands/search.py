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
import slash_commands.drop as drop


@tree.command(name="search", description="search information about a card", guild=discord.Object(id = settings.guild_id))
async def search(interaction: discord.Interaction, card: str):
    card = card.upper()
    if card not in card_info.card_info:
        await interaction.response.send_message("Card not found, or it doesn't have any information")
        return

    card_information = card_info.card_info[card]
    rarity = card[0].upper()

    user = await db.get_user(
        user_id = interaction.user.id,
        include = {
            "cards": True
        }
    )

    card_owned = card_manager.find_card(user, card)
    if card_owned is None:
        cards_owned = 0
    else:
        cards_owned = card_owned.amount

    card_count = await db.get_card_count(card)
    chances = drop.get_chances()

    embed = discord.Embed(
        title = f"Searching…",
        description = \
            f"Idol: {card_information.name}\n"
            f"Era: {card_information.era}\n"
            f"Rarity: {settings.tier_emojis[rarity]}\n"
            f"Existing copies: {card_count:,}\n"
            f"Copies owned: {cards_owned:,}",
        colour=settings.embed_color,
    )

    await interaction.response.defer()

    file = discord.File(os.path.join(drop.CARD_DIRECTORY, f"{card}.png"), filename=f"{card}.png")
    embed.set_image(url=f"attachment://{card}.png")

    await interaction.followup.send(file=file, embed=embed)
