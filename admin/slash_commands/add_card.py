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
import json


CARD_DIRECTORY = "cards"
rarities = Literal["A", "B", "C", "D", "E"]
@tree.command(name="add_card", description="create a new card for the bot", guild=discord.Object(id = settings.guild_id))
async def admin_add(interaction: discord.Interaction, rarity: rarities, id: str, group: card_info.card_groups_enum, era: card_info.card_era_enum, card: discord.Attachment, name: str):
    user_id = interaction.user.id

    name = name.capitalize()
    id = id.upper()
    group = card_info._capitalize_names(group.name)
    era = card_info._capitalize_names(era.name)

    if not check_permissions.has_permissions(
        user_id,
        "add_card"
    ):
        await interaction.response.send_message(f"You don't have permissions to use this command")
        return

    await interaction.response.send_message(f"this command still doesnt work, huge issue is that both bots run separately and they expect to only have to load some data once")
    return


    path = os.path.join(CARD_DIRECTORY, group, era)
    if not os.path.exists(path):
        await interaction.response.send_message(f"Couldn't find the folder for this group and era, make sure they're correct")
        return

    await interaction.response.defer()
    card_image = BytesIO()
    await card.save(card_image)

    card_image.seek(0)

    img = Image.open(card_image)


    card_info.idols_enum.add(name)
    card_info.cards[id] = {
        "group": group,
        "era": era,
        "name": name,
        "rarity": rarity
    }

    with open(os.path.join(path, "_cards_info.json"), "r") as f:
        info = json.load(f)

    info[id] = {
        "name": name,
        "rarity": rarity
    }

    with open(os.path.join(path, "_cards_info.json"), "w") as f:
        json.dump(info, f, indent=2)

    card_info.card_info[id] = card_info.CardInfo(**card_info.cards[id])
    card_info.non_gacha_cards_id.append(id)
    card_info.group_info[group].append(id)

    img.save(os.path.join(CARD_DIRECTORY, group, era, f"{id}.png"))


    await interaction.followup.send(content=f"Added card with id `{id.upper()}`")
