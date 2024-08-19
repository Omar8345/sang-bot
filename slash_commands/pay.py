import discord
import db
from bot import tree
from settings import settings

@tree.command(name="pay", description="pay another user currency you have collected", guild=discord.Object(id = settings.guild_id))
async def pay(interaction: discord.Interaction, user: discord.Member, amount: int):
    user_id = interaction.user.id
    other_user_id = user.id

    if amount < 0:
        await interaction.response.send_message("Can't transfer a negative amount")
        return

    user_data = await db.get_user(user_id)
    other_user_data = await db.get_user(other_user_id)

    embed = discord.Embed(
        title = "Transfer",
        colour = settings.embed_color
    )

    if user_data.balance < amount:
        await interaction.response.send_message(f"You can't transfer {amount:,} {settings.hehet_emoji}, you only have {user_data.balance:,} {settings.hehet_emoji}")
        return

    await db.update_user(
        user_id,
        new_data = {
            "balance": user_data.balance - amount
        }
    )

    await db.update_user(
        other_user_id,
        new_data = {
            "balance": other_user_data.balance + amount
        }
    )

    embed.description = f"Successfully transferred {amount:,} {settings.hehet_emoji} to <@{other_user_id}>"
    await interaction.response.send_message(embed=embed, silent=True)
