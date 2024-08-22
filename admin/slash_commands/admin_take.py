import discord
import c_card
import db
from bot import tree
from settings import settings
import admin.slash_commands.admin_gift as admin_gift
import check_permissions


BALANCE_INTEGER_LIMIT = int('1' * 63, 2)
CARD_INTEGER_LIMIT = int('1' * 31, 2)
@tree.command(name="admin_take", description="take cards or hehet from a player", guild=discord.Object(id = settings.guild_id))
async def admin_take(interaction: discord.Interaction, user: discord.Member, card: str | None = None, card_amount: int | None = 0, hehet: int | None = 0):
    user_id = interaction.user.id
    other_user_id = user.id

    if card is not None:
        card = card.upper()

    if not check_permissions.has_permissions(
        user_id,
        "admin_take"
    ):
        await interaction.response.send_message(f"You don't have permissions to use this command")
        return

    if card_amount < 0 or hehet < 0:
        await interaction.response.send_message("Use `admin_give` if you want the card_amount/hehet to be negative")
        return

    if card_amount >= CARD_INTEGER_LIMIT:
        await interaction.response.send_message(f"Card amount is too big (>{CARD_INTEGER_LIMIT:,})")
        return


    if hehet >= BALANCE_INTEGER_LIMIT:
        await interaction.response.send_message(f"Card amount is too big (>{BALANCE_INTEGER_LIMIT:,})")
        return

    other_user_data = await db.get_user(
        other_user_id
    )

    await db.update_user(
        other_user_id,
        new_data={
            "balance": other_user_data.balance - hehet
        }
    )

    if card is not None:
        if card.upper() not in admin_gift.load_cards():
            await interaction.response.send_message(f"Card `{card}` doesn't exist")
            return

        await db.add_cards(
            other_user_id,
            c_card.Card(
                user_id = other_user_id,
                card_id = card
            ),
            -card_amount
        )

    description = "Took "
    if hehet != 0:
        description += f"{hehet:,} {settings.hehet_emoji} "

    if card is not None:
        if hehet != 0:
            description += "and "
        description += f"{card_amount:,} `{card}`'s "

    description += f"from <@{other_user_id}>"
    embed = discord.Embed(
        title = "Admin Take",
        colour = settings.embed_color,
        description = description
    )

    await interaction.response.send_message(embed=embed, silent=True)
