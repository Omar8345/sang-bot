import discord
from command_handler import commands
from settings import settings
import error_handling
import slash_commands.inventory as inventory
import slash_commands.binder as binder
import slash_commands.gacha as gacha
import slash_commands.achievements as achievements


async def handle(interaction: discord.Interaction) -> None:
    custom_id = interaction.data["custom_id"] if "custom_id" in interaction.data else ""

    if custom_id == "": return

    original_user_id = None
    if custom_id.startswith("["):
        original_user_id, custom_id = custom_id[1:].split("]")
        try:
            original_user_id = int(original_user_id)
        except ValueError:
            ...

    if custom_id.startswith("inventory"):
        _, index, action = custom_id.split("%")
        index = int(index) - 1
        if action == "next":
            index += 2

        await inventory.show_inventory(interaction, page = index, edit = True)

    elif custom_id.startswith("binder"):
        _, name, index, action = custom_id.split("%")
        index = int(index) - 1
        if action == "next":
            index += 2

        await binder.display_binder(interaction, name, index = index, edit = True)

    elif custom_id.startswith("gacha_history"):
        _, index, action = custom_id.split("%")
        index = int(index) - 1
        if action == "next":
            index += 2

        await gacha.show_gacha_history(interaction, index = index, edit = True)

    elif custom_id.startswith("achievements"):
        _, index, action = custom_id.split("%")
        index = int(index) - 1
        if action == "next":
            index += 2

        await achievements.show_achievements(interaction, page = index, edit = True)