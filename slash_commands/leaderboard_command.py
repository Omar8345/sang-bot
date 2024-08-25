import discord
from bot import tree, bot
from settings import settings
import leaderboard
import card_info


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
async def cards_leaderboard(
        interaction: discord.Interaction,
        group: card_info.card_groups_enum | None = None,
        idol: str | None = None
):

    title = "Cards Leaderboard"
    if group is not None:
        title = f"Group `{group.name}` Leaderboard"

    if idol is not None:
        idol = card_info._capitalize_names(idol)
        if not hasattr(card_info.idols_enum, idol):
            await interaction.response.send_message(f"Couldn't find {idol}")
            return
        title = f"Idol `{idol}` Leaderboard"

    embed = discord.Embed(
        title = title,
        color = settings.embed_color
    )

    if idol is not None:
        result = leaderboard.load_top_idol(idol)
    elif group is not None:
        result = leaderboard.load_top_group(group.name)
    else:
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

        plural = 'ies' if (i > 1) else 'y'
        embed.add_field(
            name = f"{place}) {display_name} - {username}",
            value = f"> {i:,} cop{plural}",
            inline = False
        )

    await interaction.response.send_message(embed=embed, silent=True)

