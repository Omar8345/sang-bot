import discord
import bot
from settings import settings
import db

async def handle() -> None:
    await db.connect()

    await bot.tree.sync(guild=discord.Object(id=settings.guild_id))
