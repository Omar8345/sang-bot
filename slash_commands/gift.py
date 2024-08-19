import discord
import db
from bot import tree
from settings import settings
import card_manager


@tree.command(name="gift", description="give another user a card from your own inventory", guild=discord.Object(id = settings.guild_id))
async def gift(interaction: discord.Interaction, user: discord.Member, card: str, amount: int = 1):
    user_id = interaction.user.id
    other_user_id = user.id

    if amount <= 0:
        await interaction.response.send_message("Amount must be bigger than 0")
        return

    user_data = await db.get_user(
        user_id,
        include = {
            "cards": True
        }
    )
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

    card = card_manager.find_card(user_data, card.upper())

    if card is None:
        await interaction.response.send_message("You don't have this card")
        return

    if card.amount < amount:
        await interaction.response.send_message(f"You can't transfer {amount:,} of this card, you only have {card.amount:,}")
        return

    await db.add_cards(
        user_id,
        card,
        -amount
    )

    await db.add_cards(
        other_user_id,
        card,
        amount
    )

    embed.description = f"Successfully transferred {amount:,} `{card.card_id}`'s to <@{other_user_id}>"
    await interaction.response.send_message(embed=embed)
