import discord
import leaderboard
from command_handler import commands
import error_handling
import bot
from settings import settings
import db
from discord.ext import tasks


@tasks.loop(hours = 1, reconnect=True)
async def update_leaderboard():
    await leaderboard.calculate_leaderboards()

async def handle() -> None:
    await db.connect()
    await leaderboard.calculate_leaderboards()

    update_leaderboard.start()

    await bot.tree.sync(guild=discord.Object(id=settings.guild_id))
