import discord
from bot import tree
from settings import settings
import db
import time
import achievements_manager


WORK_COOLDOWN_SECONDS = 3_600
PAYMENT = 1_000 # how much money the user gets everytime they work

@tree.command(name="work", description="gain hehet by working", guild=discord.Object(id = settings.guild_id))
async def work(interaction: discord.Interaction):
    user_id = interaction.user.id
    cool_downs = await db.get_cooldown(user_id)

    embed = discord.Embed(
        title = "Work",
        colour = settings.embed_color
    )

    if time.time() - cool_downs.work > WORK_COOLDOWN_SECONDS: # cooldown expired
        user = await db.get_user(user_id)

        await db.update_user(user_id, {"balance": user.balance + PAYMENT})
        await db.update_cooldown(user_id, {"work": int(time.time())})

        embed.description = f"+ {PAYMENT:,} {settings.hehet_emoji}"

        await achievements_manager.add_to_progress(db, user_id, achievements_manager.HEHET_COLLECTED, PAYMENT)
        await interaction.response.send_message(embed = embed)
    else:
        next_time = cool_downs.work + WORK_COOLDOWN_SECONDS
        embed.description = f"You can only work once per hour! Try again <t:{next_time}:R>"
        await interaction.response.send_message(embed = embed)
