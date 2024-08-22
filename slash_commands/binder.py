import discord
import db
from bot import tree
from settings import settings
import os
from discord import ButtonStyle
from discord.ui import View, Button
from io import BytesIO
import group_cards


@tree.command(name="binder_create", description="create a folder with your favorite cards", guild=discord.Object(id = settings.guild_id))
async def binder_create(interaction: discord.Interaction, name: str, cards: str):
    comparison_name = name.lower()
    cards = [i for i in cards.replace(',', ' ').upper().split(" ") if len(i) > 0]

    user_id = interaction.user.id
    user = await db.get_user(
        user_id,
        include = {
            "folders": True,
            "cards": True
        }
    )

    user_folders = [i.name.lower() for i in user.folders]

    if comparison_name in user_folders:
        await interaction.response.send_message(f"You already have a folder with this name. (it's not case sensitive)")
        return

    user_cards = [i.card_id.upper() for i in user.cards]

    skipped_count = 0
    skipped_cards = []
    used_cards = []
    for card in cards:
        if card not in user_cards:
            skipped_count += 1
            skipped_cards.append(f"`{card}`")
        else:
            used_cards.append(card)


    if skipped_count == len(cards):
        await interaction.response.send_message("You don't have any of the cards you listed")
        return

    description = f"Cards: {','.join([f'`{i}`' for i in used_cards])}\n"

    if skipped_count:
        thingy = "them" if skipped_count > 1 else "it"
        description += f"-# Skipped {','.join(skipped_cards)}, cause you don't own {thingy}"


    embed = discord.Embed(
        title = f"Created a new binder named {name}",
        color = settings.embed_color,
        description = description
    )

    await db.create_folder(
        user_id,
        name,
        cards = used_cards
    )

    await interaction.response.send_message(embed=embed)


@tree.command(name="binder_delete", description="delete a folder you made", guild=discord.Object(id = settings.guild_id))
async def binder_delete(interaction: discord.Interaction, name: str):
    user_id = interaction.user.id
    user = await db.get_user(
        user_id,
        include = {
            "folders": True
        }
    )

    user_folders = [i.name.lower() for i in user.folders]

    if name.lower() not in user_folders:
        await interaction.response.send_message(f"You don't have any folder named `{name}`")
        return

    await db.delete_folder(
        user_id,
        name
    )

    await interaction.response.send_message(f"Successfully deleted folder `{name}`")


@tree.command(name="binders", description="shows your folders", guild=discord.Object(id = settings.guild_id))
async def binders(interaction: discord.Interaction, name: str | None = None):
    if name is not None:
        await display_binder(interaction, name.lower())
        return
    else:
        await display_all_binders(interaction)
        return

    await interaction.response.send_message(f"how did you even get this message? (send this to a dev)")


async def display_all_binders(interaction: discord.Interaction):
    user_id = interaction.user.id
    user = await db.get_user(
        user_id,
        include = {
            "folders": True
        }
    )

    embed = discord.Embed(
        title = "Binders",
        color = settings.embed_color
    )

    for folder in user.folders:
        number_of_cards = len(folder.cards.split(' '))
        plural = 's' if number_of_cards > 1 else ''
        embed.add_field(
            name = f"{folder.name}",
            value = f"{number_of_cards:,} card{plural}"
        )

    if len(user.folders) == 0:
        embed.description = "You don't have any binders yet, run `/binder_create` to make one"
    await interaction.response.send_message(embed = embed)


async def display_binder(interaction: discord.Interaction, name: str):
    user_id = interaction.user.id

    user = await db.get_user(
        user_id,
        include = {
            "folders": True
        }
    )

    user_folders = [i.name.lower() for i in user.folders]

    if name.lower() not in user_folders:
        await interaction.response.send_message(f"You don't have any folder named `{name}`")
        return

    binder = await db.get_folder(
        user_id,
        name
    )

    embed = discord.Embed(
        title = f"Binder {name}",
        color = settings.embed_color
    )

    cards = binder.cards.split(' ')

    await interaction.response.defer()
    cards_image = BytesIO()
    group_cards.generate_image(
        [   # first number doesnt matter as long as its not smaller than like 5 or smth idk
            [124, card] for card in cards
        ],
        cards_image
    )

    cards_image.seek(0)
    file = discord.File(cards_image, filename="img.png")

    embed.set_image(url="attachment://img.png")

    await interaction.followup.send(file = file, embed = embed)

