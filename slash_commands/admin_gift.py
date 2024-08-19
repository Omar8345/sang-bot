import discord
import c_card
import db
from bot import tree
from settings import settings
import slash_commands.drop as drop
import check_permissions


INTEGER_LIMIT = int('1' * 31, 2)

@tree.command(name="admin_gift", description="create new cards", guild=discord.Object(id = settings.guild_id))
async def admin_gift(interaction: discord.Interaction, user: discord.Member, card: str, amount: int = 1):
    user_id = interaction.user.id
    other_user_id = user.id

    card = card.upper()
    if not check_permissions.has_permissions(
        user_id,
        "admin_gift"
    ):
        await interaction.response.send_message(f"You don't have permissions to use this command")
        return


    if amount < 0:
        await interaction.response.send_message("Use `admin_take` if you want the amount to be negative")
        return

    if amount >= INTEGER_LIMIT:
        await interaction.response.send_message(f"Amount is too big (>{INTEGER_LIMIT:,})")
        return

    if card.upper() not in drop.load_cards():
        await interaction.response.send_message(f"Card `{card}` doesn't exist")
        return

    other_user_data = await db.get_user(
        other_user_id,
        include = {
            "cards": True
        }
    )

    embed = discord.Embed(
        title = "Transfer",
        colour = settings.embed_color
    )

    await db.add_cards(
        other_user_id,
        c_card.Card(
            user_id = other_user_id,
            card_id = card
        ),
        amount
    )

    embed.description = f"Gave {amount:,} `{card}`'s to <@{other_user_id}>"
    await interaction.response.send_message(embed=embed, silent=True)
