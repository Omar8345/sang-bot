import discord
from bot import tree, bot
from settings import settings
import leaderboard


@tree.command(name="leaderboard_hehet", description="see the top players", guild=discord.Object(id = settings.guild_id))
async def hehet_leaderboard(interaction: discord.Interaction):

    embed = discord.Embed(
        title = "Hehet Leaderboard",
        color = settings.embed_color
    )

    result = leaderboard.load_top_hehet()
    place = 0
    for i, v in result:
        place += 1
        user = bot.get_user(v)
        if user is None:
            username = "unknown"
            display_name = "unkown"
        else:
            username = user.name
            display_name = user.display_name

        embed.add_field(
            name = f"{place}) {display_name} - {username}",
            value = f"> {i:,} {settings.hehet_emoji}",
            inline = False
        )

    await interaction.response.send_message(embed=embed, silent=True)

@tree.command(name="leaderboard_cards", description="see the top players", guild=discord.Object(id = settings.guild_id))
async def cards_leaderboard(interaction: discord.Interaction):

    embed = discord.Embed(
        title = "Cards Leaderboard",
        color = settings.embed_color
    )

    result = leaderboard.load_top_cards()
    place = 0
    for i, v in result:
        place += 1
        user = bot.get_user(v)
        if user is None:
            username = "unknown"
            display_name = "unkown"
        else:
            username = user.name
            display_name = user.display_name

        plural = 's' if (i > 1) else ''
        embed.add_field(
            name = f"{place}) {display_name} - {username}",
            value = f"> {i:,} card{plural}",
            inline = False
        )

    await interaction.response.send_message(embed=embed, silent=True)

