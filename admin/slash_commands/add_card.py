import os
import discord
import c_card
from bot import tree
from settings import settings
import check_permissions
from PIL import Image
import card_info
from io import BytesIO


CARD_DIRECTORY = "cards"
@tree.command(name="add_card", description="create a new card for the bot", guild=discord.Object(id = settings.guild_id))
async def admin_add(interaction: discord.Interaction, id: str, group: str, name: str, era: str, card: discord.Attachment):
    user_id = interaction.user.id

    if not check_permissions.has_permissions(
        user_id,
        "add_card"
    ):
        await interaction.response.send_message(f"You don't have permissions to use this command")
        return

    card_image = BytesIO()
    await card.save(card_image)

    await interaction.response.defer()
    card_image.seek(0)

    img = Image.open(card_image)
    img.save(os.path.join(CARD_DIRECTORY, f"{id.upper()}.png"))

    card_info.add_card(
        id = id,
        name = name,
        era = era,
        group = group
    )


    await interaction.followup.send(content=f"Added card with id `{id.upper()}`")

