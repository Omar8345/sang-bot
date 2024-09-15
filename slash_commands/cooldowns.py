import discord
from bot import tree
from settings import settings
import db
import achievements_manager
from c_cooldown import *

@tree.command(name="cooldowns", description="check the cooldown of commands", guild=discord.Object(id = settings.guild_id))
async def work(interaction: discord.Interaction):
    user_id = interaction.user.id
    cool_downs = await db.get_cooldown(user_id)

    embed = discord.Embed(
        title = "Work",
        colour = settings.embed_color
    )

    embed.add_field(
        name = "Daily",
        value = f"available <t:{cool_downs.daily + DAILY_COOLDOWN_SECONDS}:R>",
        inline = False
    )
    embed.add_field(
        name = "Work",
        value = f"available <t:{cool_downs.work + WORK_COOLDOWN_SECONDS}:R>",
        inline = False
    )
    embed.add_field(
        name = "Drop",
        value = f"available <t:{cool_downs.drop + DROP_COOLDOWN_SECONDS}:R>",
        inline = False
    )

    await interaction.response.send_message(embed = embed)
