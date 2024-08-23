import discord
import achievements_manager
import c_card
from bot import tree
from settings import settings
import db


@tree.command(name="buy", description="buy a card from another user or the bot", guild=discord.Object(id = settings.guild_id))
async def buy(interaction: discord.Interaction, item_id: str, amount: int):
    bad_id = False

    if amount <= 0:
        await interaction.response.send_message(f"Amount must be bigger than 0")
        return

    if item_id != "buds" and not item_id.isnumeric():
        bad_id = True

    if item_id == "buds":
        await buy_buds(interaction, amount)
        return


    user_id = interaction.user.id
    user = await db.get_user(
        user_id,
        include = {
            "shop": True
        }
    )

    card = await db.get_sold_card(item_id)

    if card.user_id == user_id:
        await interaction.response.send_message("You can't buy from yourself")
        return

    if card is None:
        bad_id = True

    if bad_id:
        await interaction.response.send_message(f"ID `{item_id}` doesn't exist")
        return

    price = card.price * amount
    if price > user.balance:
        await interaction.response.send_message(
            f"You can't afford this ({price:,} {settings.hehet_emoji}), you only have {user.balance:,} {settings.hehet_emoji}"
        )
        return

    if amount > card.amount:
        await interaction.response.send_message(f"You can't buy {amount} of this card, there's only {card.amount}")
        return

    await db.update_user(
        user_id,
        new_data = {
            "balance": user.balance - price
        }
    )


    other_user = await db.get_user(card.user_id)
    await db.update_user(
        card.user_id,
        new_data={
            "balance": other_user.balance + price
        }
    )

    await db.add_cards(
        user_id = user_id,
        card = c_card.Card(user_id = user_id, card_id = card.card_id),
        amount = amount
    )

    await db.update_sold_cards(
        item_id,
        new_data = {
            "amount": card.amount - amount
        }
    )

    await achievements_manager.add_to_progress(db, user_id, achievements_manager.HEHET_SPENT, price)
    await interaction.response.send_message(f"Successfully bought {amount:,} cards for {price:,} {settings.hehet_emoji}")


async def buy_buds(interaction: discord.Interaction, amount: int):
    user_id = interaction.user.id
    price = amount * settings.bud_price

    user = await db.get_user(
        user_id
    )

    if price > user.balance:
        await interaction.response.send_message(
            f"You can't afford this ({price:,} {settings.hehet_emoji}), you only have {user.balance:,} {settings.hehet_emoji}"
        )
        return

    await db.update_user(
        user_id,
        new_data = {
            "buds": user.buds + amount,
            "balance": user.balance - price
        }
    )
    await achievements_manager.add_to_progress(db, user_id, achievements_manager.HEHET_SPENT, price)
    await interaction.response.send_message(f"Successfully bought {amount:,} buds for {price:,} {settings.hehet_emoji}")