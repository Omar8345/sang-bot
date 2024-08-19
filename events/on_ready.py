import discord
from command_handler import commands
import error_handling
import bot
from settings import settings
import db


async def handle() -> None:
    await db.connect()
    await bot.tree.sync(guild=discord.Object(id=settings.guild_id))
