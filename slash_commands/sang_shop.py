import uuid
import discord
import prisma
import card_manager
import db
from bot import tree
from settings import settings
from typing import Literal
import os
import slash_commands.shop as shop
from bot import bot


@tree.command(name="sang_shop", description="view the bot's shop", guild=discord.Object(id = settings.guild_id))
async def sang_shop(
        interaction: discord.Interaction
    ):
    await shop.display_shop(
        interaction,
        bot.user
    )

