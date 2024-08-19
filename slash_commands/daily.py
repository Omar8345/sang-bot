import discord
import probability_stuff
from bot import tree
from settings import settings
import db
import time
from slash_commands import drop
import c_card
import os
import card_info


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

        chances = drop.get_chances()

        card_id = probability_stuff.get_random_card(chances, card_info.non_gacha_cards_id).upper()
        card_rarity = card_id[0]

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

        embed.description = f"+ {DAILY_HEHET_REWARD:,} {settings.hehet_emoji}\n"
        embed.description += f"+ {settings.tier_emojis[card_rarity]} Tier card (`{card_id}`)"

        await interaction.response.defer()
        file = discord.File(os.path.join(drop.CARD_DIRECTORY, f"{card_id}.png"), f"{card_id}.png")
        embed.set_image(url=f"attachment://{card_id}.png")

        await interaction.followup.send(file=file, embed=embed)
    else:
        next_time = cool_downs.daily + DAILY_COOLDOWN_SECONDS
        embed.description = f"You can only claim daily once per day! Try again <t:{next_time}:R>"
        await interaction.response.send_message(embed = embed)
