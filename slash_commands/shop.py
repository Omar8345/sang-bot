import uuid

import discord
import prisma

import bot
import card_manager
import db
from bot import tree
from settings import settings
from typing import Literal
import os


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

@tree.command(name="shop", description="view an user's shop", guild=discord.Object(id = settings.guild_id))
async def shop(
        interaction: discord.Interaction,
        user: discord.Member | None = None
    ):
    await display_shop(interaction, user)


def _find_image(name: str) -> str | None:
    for image in os.listdir(SHOP_IMAGES_DIRECTORY):
        if image.startswith(name):
            return image
    return None


async def display_shop(
        interaction: discord.Interaction,
        user: discord.Member | None = None
    ):

    if user is None:
        user_id = interaction.user.id
        username = interaction.user.name
    else:
        user_id = user.id
        username = user.name
    if user_id == bot.bot.user.id:
        user_id = -1


    shop = await db.get_shop(
        user_id,
        include = {
            "cards": True
        }
    )

    embed = discord.Embed(
        title = f"{username}'s shop",
        description = shop.bio,
        colour = settings.embed_color
    )

    if user_id == -1:
        embed.add_field(
            name = f"buds - {settings.bud_price:,} {settings.hehet_emoji}",
            value = f"id: buds\namount: infinite"
        )

    for sold_card in shop.cards:
        id = sold_card.item_id
        card_id = sold_card.card_id
        amount = sold_card.amount
        price = sold_card.price

        if shop.user_id == -1 and amount < 0:
            amount = "infinite"
        else:
            amount = f"{amount:,}"

        embed.add_field(
            name = f"`{card_id}` - {price:,} {settings.hehet_emoji}",
            value = f"id: {id}\namount: {amount}"
        )

    kwargs = {
        "embed": embed
    }

    await interaction.response.defer()

    image = _find_image(shop.image)
    if shop.image != "none" and image is not None:
        file = discord.File(os.path.join(SHOP_IMAGES_DIRECTORY, image), filename=image)
        embed.set_image(url=f"attachment://{image}")
        kwargs["file"] = file

    await interaction.followup.send(**kwargs)


@tree.command(name="shop_add", description="add cards to your shop", guild=discord.Object(id = settings.guild_id))
async def shop_add(
        interaction: discord.Interaction,
        card: str,
        amount: int,
        price: int
    ):
    card = card.upper()
    user_id = interaction.user.id

    if amount <= 0:
        await interaction.response.send_message("Amount must be bigger than 0")
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

    user = await db.get_user(
        user_id,
        include = {
            "cards": True,
            "shop": True
        }
    )

    card_obj = card_manager.find_card(user, card)
    if card_obj is None:
        await interaction.response.send_message(f"Can't sell card `{card}` if you don't have it")
        return

    if card_obj.amount < amount:
        await interaction.response.send_message(
            f"You can't sell {amount:,} of this card, you only have {card_obj.amount:,}")
        return

    await db.add_cards(
        user_id,
        card_obj,
        -amount
    )

    await db.add_to_shop(
        user_id = user_id,
        card_id = card,
        amount = amount,
        price = price
    )

    await interaction.response.send_message(f"Added {amount:,} `{card}` for {price:,} each to your shop")


@tree.command(name="shop_bio", description="edit your shop's description and image", guild=discord.Object(id = settings.guild_id))
async def shop_bio(
        interaction: discord.Interaction,
        bio: str | None = None,
        image: discord.Attachment | None = None
    ):
    if bio is None and image is None:
        await interaction.response.send_message("Choose at least 1 field (`bio` or `image`)")
        return

    user_id = interaction.user.id

    shop = await db.get_shop(
        user_id
    )

    if bio is not None:
        if len(bio) > SHOP_BIO_CHARACTER_LIMIT:
            await interaction.response.send_message(f"Bio can't be longer than {SHOP_BIO_CHARACTER_LIMIT} characters")
            return

        await db.update_shop(
            user_id,
            new_data={
                "bio": bio
            }
        )
        if image is None:
            await interaction.response.send_message(f"Changed shop bio to `{bio}`")
            return

    if image is not None:
        image_name = str(uuid.uuid4())

        extension = image.filename.split(".")[-1]

        if extension not in ACCEPTED_IMAGE_EXTENSIONS:
            await interaction.response.send_message(f"File extension is not in the allowed list\nMust be one of these: {extensions_list_str}")
            return

        await interaction.response.defer()

        await image.save(os.path.join(SHOP_IMAGES_DIRECTORY, f"{image_name}.{extension}"))

        await db.update_shop(
            user_id,
            new_data = {
                "image": image_name
            }
        )

        if bio is None:
            await interaction.followup.send("Changed your shop's image")
            return
        else:
            await interaction.followup.send("Changed your shop's image and bio")
