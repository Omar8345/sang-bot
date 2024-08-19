import discord
from bot import tree
from settings import settings

@tree.command(name="ping", description="check if the bot is online", guild=discord.Object(id = settings.guild_id))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")
