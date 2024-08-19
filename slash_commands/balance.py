import discord
from bot import tree
from settings import settings
import db


@tree.command(name="balance", description="check if the bot is online", guild=discord.Object(id = settings.guild_id))
async def balance(interaction: discord.Interaction):
    user = await db.get_user(interaction.user.id)

    embed = discord.Embed(
        title="Balance",
        colour=settings.embed_color,
        description=f"You have `{user.balance:,}` {settings.hehet_emoji} and `{user.buds:,}` buds"
    )

    await interaction.response.send_message(embed=embed)
