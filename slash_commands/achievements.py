import discord
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


ACHIEVEMENTS_PER_PAGE = 8


@tree.command(name="achievements", description="check your achievements", guild=discord.Object(id = settings.guild_id))
async def achievements(interaction: discord.Interaction): # old method: ', card: str | None = None):'
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

    embed = discord.Embed(
        title = "Achievements",
        color = settings.embed_color
    )

    user_data.cards.sort(
        key = (lambda x: rank_order[x.card_id[0].upper()])
    )


    # hey dont forget to fill me -w-
    for achievement in achievements:
        ...

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
            label = f"{page + 1} / {math.ceil(len(user_data.cards) / ACHIEVEMENTS_PER_PAGE)}",
            disabled = True
        )
    )

    view.add_item(
        Button(
            style = ButtonStyle.primary,
            label = ">",
            custom_id = f"[{user_id}]achievements%{page + 1}%next",
            disabled = (page + 1 == math.ceil((len(user_data.cards) / ACHIEVEMENTS_PER_PAGE)))
        )
    )

    if edit:
        await interaction.response.defer()
        await interaction.message.edit(embed = embed, view = view)
    else:
        await interaction.response.send_message(embed = embed, view = view)
