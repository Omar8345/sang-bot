import uuid
import discord
import bot
import card_info
import card_manager
import db
from bot import tree, bot
from settings import settings
from typing import Literal
import os
import check_permissions


SHOP_IMAGES_DIRECTORY = "shop_images"
ACCEPTED_IMAGE_EXTENSIONS = [
    "png",
    "jpeg",
    "jpg",
    "webp"
]
SHOP_BIO_CHARACTER_LIMIT = 200
INTEGER_LIMIT = int('1' * 31, 2)

extensions_list_str = ", ".join([f"`.{i}`" for i in ACCEPTED_IMAGE_EXTENSIONS])

@tree.command(name="admin_shop", description="add the bot shop", guild=discord.Object(id = settings.guild_id))
async def admin_shop(
        interaction: discord.Interaction,
        card: str,
        amount: int,
        price: int
    ):

    card = card.upper()
    user_id = interaction.user.id

    if not check_permissions.has_permissions(
        user_id,
        "admin_shop"
    ):
        await interaction.response.send_message(f"You don't have permissions to use this command")
        return

    if amount >= INTEGER_LIMIT:
        await interaction.response.send_message(f"Amount is too big (>{INTEGER_LIMIT:,})")
        return

    if price < 0:
        await interaction.response.send_message("Price can't be negative")
        return

    if price >= INTEGER_LIMIT:
        await interaction.response.send_message(f"Price is too big (>{INTEGER_LIMIT:,})")
        return


    existing_cards = card_info.all_cards
    if card not in existing_cards:
        await interaction.response.send_message(f"Card `{card}` doesn't exist")
        return

    await db.add_to_shop(
        user_id = -1,
        card_id = card,
        amount = amount,
        price = price
    )

    if amount < 0:
        amount = "infinite"
    else:
        amount = f"{amount:,}"

    await interaction.response.send_message(f"Added {amount} `{card}` for {price:,} each to the bot shop")


@tree.command(name="admin_shop_remove", description="remove cards from the bot shop", guild=discord.Object(id = settings.guild_id))
async def admin_shop(
        interaction: discord.Interaction,
        item_id: int
    ):
    user_id = interaction.user.id

    if not check_permissions.has_permissions(
        user_id,
        "admin_shop_remove"
    ):
        await interaction.response.send_message(f"You don't have permissions to use this command")
        return

    card = await db.get_sold_card(item_id)
    if card is None:
        await interaction.response.send_message(f"ID not found")
        return

    await db.update_sold_cards(
        card_id = item_id,
        new_data = {
            "amount": 0
        }
    )

    await interaction.response.send_message(f"Removed `{item_id}` from the bot shop")
