import discord
import db
import reminder_handler
from bot import tree
from settings import settings
from typing import Literal
import time


@tree.command(name="reminder", description="check if the bot is online", guild=discord.Object(id = settings.guild_id))
async def reminders(interaction: discord.Interaction, name: Literal["drop", "work", "daily", "all"], enable: bool):
    user_id = interaction.user.id

    cooldowns = await db.get_cooldown(user_id = user_id)

    if name == "all":
        await db.update_reminder(
            user_id=interaction.user.id,
            new_data={
                "drop": +enable,
                "work": +enable,
                "daily": +enable
            }
        )
        for _name, cooldown in [
            ["drop", cooldowns.drop],
            ["work", cooldowns.work],
            ["daily", cooldowns.daily]
        ]:
            if time.time() - cooldown >= reminder_handler.reminder_times[_name] - 120:
                reminder_handler.quick_reminders.append(
                    [_name, user_id, cooldown]
                )
    else:
        await db.update_reminder(
            user_id = interaction.user.id,
            new_data = {
                name: +enable
            }
        )

        if time.time() - getattr(cooldowns, name) >= reminder_handler.reminder_times[name] - 120:
            reminder_handler.quick_reminders.append(
                [name, user_id, getattr(cooldowns, name)]
            )

    if enable:
        enabled_text = "Enabled"
    else:
        enabled_text = "Disabled"

    plural = "s" if name == "all" else ""
    await interaction.response.send_message(f"{enabled_text} {name} reminder{plural}")
