import random
import discord
from bot import tree
from settings import settings
import db
import time
import achievements_manager
from c_cooldown import WORK_COOLDOWN_SECONDS


PAYMENT = 1_000 # how much money the user gets everytime they work
SUCCESS_1 = 1
SUCCESS_2 = 2
FAIL_1 = 3
FAIL_2 = 4
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

        await db.update_cooldown(user_id, {"work": int(time.time())})
        outcome = random.randint(1, 4)

        if outcome == SUCCESS_1:
            embed.description = "Gotta work, gotta make that money make purse "

        if outcome == SUCCESS_2:
            embed.description = "While looking for Utopia you found "

        if outcome == FAIL_1:
            embed.description = "Just like inception, you got lost in a dream "

        if outcome == FAIL_2:
            embed.description = "You know that I’m not okay "

        if outcome <= SUCCESS_2:
            embed.description += f"+{PAYMENT:,} {settings.hehet_emoji}"
            await db.update_user(user_id, {"balance": user.balance + PAYMENT})
            await achievements_manager.add_to_progress(db, user_id, achievements_manager.HEHET_COLLECTED, PAYMENT)
        else:
            embed.description += f"(no hehets given)"

        await interaction.response.send_message(embed = embed)
    else:
        next_time = cool_downs.work + WORK_COOLDOWN_SECONDS
        embed.description = f"You can only work once per hour! Try again <t:{next_time}:R>"
        await interaction.response.send_message(embed = embed)
