from discord.ext import tasks
from discord import utils
import bot
from c_cooldown import *
import db
import time

reminder_times = {
   "daily" : DAILY_COOLDOWN_SECONDS,
    "drop" : DROP_COOLDOWN_SECONDS,
    "work" : WORK_COOLDOWN_SECONDS
}

reminder_text = {
   "daily" : "Don't forget to collect your daily reward",
    "drop" : "Don't forget to run `drop`",
    "work" : "Don't forget to run `work`"
}

quick_reminders = []

TIME_OFFSET = 120
@tasks.loop(minutes = 2)
async def reminder_loop():
    if reminder_loop.current_loop == 0:
        quick_reminders_loop.start()

    # WORK REMINDERS
    users_with_work_reminders_enabled = [
        user.user_id \
        for user in (
            await db.db.reminder.find_many(
                where = {
                    "work": 1
                }
            )
        )
    ]

    work_time = int(time.time() - WORK_COOLDOWN_SECONDS + TIME_OFFSET)
    work_reminders = await db.db.cooldown.find_many(
        where = {
            "work": {
                "lte": work_time
            },
            "user_id": {
                "in": users_with_work_reminders_enabled
            }
        }
    )

    for reminder in work_reminders:
        await db.update_reminder(
            user_id = reminder.user_id,
            new_data = {
                "work": 2
            }
        )
        quick_reminders.append([
            "work",
            reminder.user_id,
            reminder.work
        ])

    # DAILY REMINDERS
    users_with_daily_reminders_enabled = [
        user.user_id \
        for user in (
            await db.db.reminder.find_many(
                where={
                    "daily": 1
                }
            )
        )
    ]

    daily_time = int(time.time() - DAILY_COOLDOWN_SECONDS + TIME_OFFSET)
    daily_reminders = await db.db.cooldown.find_many(
        where={
            "daily": {
                "lte": daily_time
            },
            "user_id": {
                "in": users_with_daily_reminders_enabled
            }
        }
    )

    for reminder in daily_reminders:
        await db.update_reminder(
            user_id = reminder.user_id,
            new_data = {
                "daily": 2
            }
        )
        quick_reminders.append([
            "daily",
            reminder.user_id,
            reminder.daily
        ])

    # DROP REMINDERS
    users_with_drop_reminders_enabled = [
        user.user_id \
        for user in (
            await db.db.reminder.find_many(
                where={
                    "drop": 1
                }
            )
        )
    ]

    drop_time = int(time.time() - DROP_COOLDOWN_SECONDS + TIME_OFFSET)
    drop_reminders = await db.db.cooldown.find_many(
        where = {
            "drop": {
                "lte": drop_time
            },
            "user_id": {
                "in": users_with_drop_reminders_enabled
            }
        }
    )

    for reminder in drop_reminders:
        await db.update_reminder(
            user_id = reminder.user_id,
            new_data = {
                "drop": 2
            }
        )
        quick_reminders.append([
            "drop",
            reminder.user_id,
            reminder.drop
        ])


@tasks.loop(seconds = 2)
async def quick_reminders_loop():
    now = time.time()
    i = 0
    while i < len(quick_reminders):
        reminder, user, expires = quick_reminders[i]
        if now - expires >= reminder_times[reminder]:
            quick_reminders.pop(i)
            try:
                await bot.bot.get_user(user).send(reminder_text[reminder])
            except Exception as e:
                print(e)

            i -= 1
        i += 1
