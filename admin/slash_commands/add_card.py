import os
import discord
import c_card
from bot import tree
from settings import settings
import check_permissions
from PIL import Image
import card_info
from io import BytesIO
import card_info
from typing import Literal


CARD_DIRECTORY = "cards"
rarities = Literal["SS", "S", "A", "B", "C", "D", "E"]
@tree.command(name="add_card", description="create a new card for the bot", guild=discord.Object(id = settings.guild_id))
async def admin_add(interaction: discord.Interaction, rarity: rarities, id: str, group: card_info.card_groups_enum, era: card_info.card_era_enum, card: discord.Attachment, name: str):
    user_id = interaction.user.id

    name = name.capitalize()
    id = id.upper()
    group = card_info._capitalize_names(group)
    era = card_info._capitalize_names(era)

    if not check_permissions.has_permissions(
        user_id,
        "add_card"
    ):
        await interaction.response.send_message(f"You don't have permissions to use this command")
        return

    await interaction.response.send_message(f"this is almost done")
    return

    card_image = BytesIO()
    await card.save(card_image)

    await interaction.response.defer()
    card_image.seek(0)

    img = Image.open(card_image)

    path = os.path.join(CARD_DIRECTORY, group.name, era.name)
    if not os.path.exists(path):
        await interaction.response.send_message(f"Couldn't find the folder for this group and era, make sure they're correct")
        return

    card_info.idols_enum.add(name)
    img.save(os.path.join(CARD_DIRECTORY, group.name, era.name))

    card_info.add_card(
        id = id,
        name = name,
        era = era,
        group = group
    )


    await interaction.followup.send(content=f"Added card with id `{id.upper()}`")

