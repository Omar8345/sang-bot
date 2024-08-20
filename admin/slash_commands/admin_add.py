import discord
import c_card
import db
from bot import tree
from settings import settings
import slash_commands.drop as drop
import check_permissions


INTEGER_LIMIT = int('1' * 63, 2)
@tree.command(name="admin_add", description="give an user currency from the bot", guild=discord.Object(id = settings.guild_id))
async def admin_add(interaction: discord.Interaction, user: discord.Member, amount: int):
    user_id = interaction.user.id
    other_user_id = user.id

    if not check_permissions.has_permissions(
        user_id,
        "admin_add"
    ):
        await interaction.response.send_message(f"You don't have permissions to use this command")
        return

    if amount < 0:
        await interaction.response.send_message("Use `admin_take` if you want the amount to be negative")
        return

    if amount >= INTEGER_LIMIT:
        await interaction.response.send_message(f"Amount is too big (>{INTEGER_LIMIT:,})")
        return

    other_user_data = await db.get_user(
        other_user_id
    )


    await db.update_user(
        other_user_id,
        new_data={
            "balance": other_user_data.balance + amount
        }
    )

    embed = discord.Embed(
        title = "Transfer",
        colour = settings.embed_color,
        description = f"Gave {amount:,} {settings.hehet_emoji} to <@{other_user_id}>"
    )

    await interaction.response.send_message(embed=embed, silent=True)
