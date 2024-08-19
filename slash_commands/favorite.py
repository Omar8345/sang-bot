import discord
import slash_commands.drop as drop
import card_manager
import db, os
from bot import tree
from settings import settings


@tree.command(name="favorite", description="showcases the card on your profile", guild=discord.Object(id = settings.guild_id))
async def ping(interaction: discord.Interaction, card: str):
    user_id = interaction.user.id
    user = await db.get_user(
        user_id,
        include = {
            "cards": True
        }
    )

    card = card.upper()

    if card_manager.find_card(user, card) is None:
        await interaction.response.send_message("You don't have this card")
        return

    await db.update_profile(
        user_id,
        new_data = {
            "favorite": card
        }
    )

    embed = discord.Embed(
        title = "Favorite",
        colour = settings.embed_color,
        description = f"`{card}` is now displayed in your profile"
    )

    await interaction.response.defer()

    file = discord.File(os.path.join(drop.CARD_DIRECTORY, f"{card}.png"), filename=f"{card}.png")

    embed.set_image(url=f"attachment://{card}.png")
    await interaction.followup.send(file=file, embed=embed)
