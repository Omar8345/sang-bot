import discord
import leaderboard
from command_handler import commands
import error_handling
import bot
from settings import settings
import db
from discord.ext import tasks
import reminder_handler
import card_info


@tasks.loop(hours = 1, reconnect=True)
async def update_leaderboard():
    await leaderboard.calculate_leaderboards()


@tasks.loop(minutes = 5)
async def update_cards():
    card_info.load_card_info()

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
        update_cards.start()

        await bot.tree.sync(guild=discord.Object(id=settings.guild_id))

    count += 1

    card_info.load_card_info()
