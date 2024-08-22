import discord
from bot import tree
from settings import settings
import os
import db
import card_manager


@tree.command(name="profile", description="view an user's profile", guild=discord.Object(id = settings.guild_id))
async def profile(interaction: discord.Interaction, bio: str | None = None, user: discord.Member | None = None):
    user_id = interaction.user.id
    username = interaction.user.name
    if bio is not None:
        await set_profile(interaction, bio)
        return
    elif user is not None:
        user_id = user.id
        username = user.name

    user_data = await db.get_user(
        user_id,
        include = {
            "cards": True
        }
    )

    user_profile = await db.get_profile(
        user_id
    )

    embed = discord.Embed(
        title = f"{username}'s profile",
        colour = settings.embed_color,
        description = user_profile.bio
    )

    kwargs = {
        "embed": embed
    }

    await interaction.response.defer()

    if user_profile.favorite != "none":
        card_id = user_profile.favorite

        file = discord.File(card_manager.get_card_image_from_id(card_id), f"{card_id}.png")
        embed.set_image(url=f"attachment://{card_id}.png")

        kwargs["file"] = file

    embed.add_field(
        name = f"{len(user_data.cards)} different cards",
        value = f"{card_manager.count_cards(user_data):,} cards",
        inline = False
    )

    embed.add_field(
        name = f"balance",
        value = f"{user_data.balance:,} {settings.hehet_emoji}",
        inline = False
    )
    await interaction.followup.send(**kwargs)


async def set_profile(interaction: discord.Interaction, bio: str):
    user_id = interaction.user.id

    if len(bio) > 150:
        await interaction.response.send_message(f"Bio can't be longer than 150 characters")
        return

    await db.update_profile(
        user_id,
        new_data = {
            "bio": bio
        }
    )

    await interaction.response.send_message(f"Changed bio to `{bio}`")
