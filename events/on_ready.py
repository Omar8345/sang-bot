import discord
import leaderboard
from command_handler import commands
import error_handling
import bot
from settings import settings
import db
from discord.ext import tasks
import reminder_handler


@tasks.loop(hours = 1, reconnect=True)
async def update_leaderboard():
    await leaderboard.calculate_leaderboards()


count = 0
async def handle() -> None:
    global count
    try:
        await db.connect()
    except Exception as e:
        print(e)

    try:
        await leaderboard.calculate_leaderboards()
    except Exception as e:
        print(e)

    if count == 0:
        update_leaderboard.start()

        reminder_handler.reminder_loop.start()

        await bot.tree.sync(guild=discord.Object(id=settings.guild_id))

    count += 1
