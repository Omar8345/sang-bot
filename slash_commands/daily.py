import discord
import achievements_manager
import probability_stuff
from bot import tree
from settings import settings
import db
import time
import c_card
import os
import card_info
import card_manager


DAILY_COOLDOWN_SECONDS = 24 * 3_600
DAILY_HEHET_REWARD = 25_000

@tree.command(name="daily", description="claim free daily rewards", guild=discord.Object(id = settings.guild_id))
async def daily(interaction: discord.Interaction):
    user_id = interaction.user.id
    cool_downs = await db.get_cooldown(user_id)

    embed = discord.Embed(
        title = "Daily",
        color = settings.embed_color
    )
    if time.time() - cool_downs.daily > DAILY_COOLDOWN_SECONDS:
        user = await db.get_user(user_id)

        chances = probability_stuff.get_chances()

        card_id = probability_stuff.get_random_card(chances, card_info.non_gacha_cards_id).upper()
        card_rarity = card_info.card_info[card_id.upper()].rarity

        await db.add_cards(
            user_id = user_id,
            card = c_card.Card(
                user_id = user_id,
                card_id = card_id
            )
        )

        await db.update_user(
            user_id,
            {
                "balance": user.balance + DAILY_HEHET_REWARD
            }
        )

        await db.update_cooldown(user_id, {"daily": int(time.time())})
        await achievements_manager.add_to_progress(db, user_id, achievements_manager.HEHET_COLLECTED, DAILY_HEHET_REWARD)

        embed.description = f"+ {DAILY_HEHET_REWARD:,} {settings.hehet_emoji}\n"
        embed.description += f"+ {settings.tier_emojis[card_rarity]} Tier card (`{card_id}`)"

        await interaction.response.defer()
        file = discord.File(card_manager.get_card_image_from_id(card_id), f"{card_id}.png")
        embed.set_image(url=f"attachment://{card_id}.png")

        await interaction.followup.send(file=file, embed=embed)
    else:
        next_time = cool_downs.daily + DAILY_COOLDOWN_SECONDS
        embed.description = f"You can only claim daily once per day! Try again <t:{next_time}:R>"
        await interaction.response.send_message(embed = embed)
