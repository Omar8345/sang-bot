import discord
import c_card
import db
from bot import tree
from settings import settings
import card_manager


@tree.command(name="gift", description="give another user cards from your own inventory", guild=discord.Object(id = settings.guild_id))
async def gift(interaction: discord.Interaction, user: discord.Member, cards: str):
    user_id = interaction.user.id
    other_user_id = user.id

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

    cards_info = cards.split(",")
    cards = []
    try:
        for i in cards_info:
            info = i.rstrip(" ").lstrip(" ").split(" ")

            if len(info) > 2:
                raise Exception("why are there more than 1 spaces")

            if len(info) == 1:
                cards.append([1, info[0].upper()])
            else:
                cards.append([int(info[0]), info[1].upper()])


    except Exception:
        await interaction.response.send_message(
            f"You wrote 'cards' wrong, please follow this template `<amount> <card id>`\n"
            f"example: `2 ASHDKK, DSTYJN, 5 ASHDNO`"
        )
        return

    for count, card in cards:
        found_card = card_manager.find_card(user_data, card.upper())

        if found_card is None:
            await interaction.response.send_message(f"You don't have this card `{card}`")
            return
        elif found_card.amount < count:
            await interaction.response.send_message(f"You can't send {count:,} of `{card}` if you only have {found_card.amount:,}")
            return

    for amount, card in cards:
        card = c_card.Card(
            user_id = user_id,
            card_id = card
        )
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

    formatted_cards = ", ".join([f"{amount} {card}" for amount, card in cards])
    embed.description = f"Successfully transferred `{formatted_cards}` to <@{other_user_id}>"
    await interaction.response.send_message(embed=embed)
