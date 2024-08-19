import discord
from command_handler import commands
from settings import settings
import error_handling


async def handle(message: discord.Message) -> None:
    # doesnt respond to bots
    if message.author.bot: return

    # checks if the prefix is correct
    if not message.content.startswith(settings.prefix): return

    command, *args = message.content[len(settings.prefix):].split()

    # can be replaced with a notice
    if command not in commands: return

    try:
        await commands[command](message, args)
    except Exception as e:
        error_handling.log_error(e)
