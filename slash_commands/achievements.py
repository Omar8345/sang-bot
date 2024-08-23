import discord
import achievements_manager
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


ACHIEVEMENTS_PER_PAGE = 5


@tree.command(name="achievements", description="check your achievements", guild=discord.Object(id = settings.guild_id))
async def achievements(interaction: discord.Interaction):
    await show_achievements(interaction)


async def show_achievements(interaction: discord.Interaction, page: int = 1, edit: bool = False):
    page -= 1
    if page < 0:
        return

    user_id = interaction.user.id
    user_data = await db.get_user(
        user_id,
        include = {
            "achievements": True
        }
    )

    # loads them just in case they don't exist
    await db.get_achievements(user_id = user_id)

    achievements_ = await achievements_manager.get_achievement_progress(user_data, (page * ACHIEVEMENTS_PER_PAGE, (page + 1) * ACHIEVEMENTS_PER_PAGE))

    embed = discord.Embed(
        title = "Achievements",
        color = settings.embed_color
    )


    # hey dont forget to fill me -w-
    for achievement, progress in achievements_:
        embed.add_field(
            name = achievement,
            value = progress,
            inline = False
        )

    view = View(timeout=60)
    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = "<",
            custom_id = f"[{user_id}]achievements%{page + 1}%back",
            disabled = (page == 0)
        )
    )

    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = f"{page + 1} / {math.ceil(len(achievements_manager.achievement_names) / ACHIEVEMENTS_PER_PAGE)}",
            disabled = True
        )
    )

    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = ">",
            custom_id = f"[{user_id}]achievements%{page + 1}%next",
            disabled = (page + 1 == math.ceil(len(achievements_manager.achievement_names) / ACHIEVEMENTS_PER_PAGE))
        )
    )

    if edit:
        await interaction.response.defer()
        await interaction.message.edit(embed = embed, view = view)
    else:
        await interaction.response.send_message(embed = embed, view = view)
