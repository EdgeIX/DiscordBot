#!/usr/bin/env python3
import asyncio
import aiohttp

import discord
from discord import app_commands
from discord.ext import commands

from utils.functions import format_message
from utils.constants import ASN_REGEX
from utils.config import get_conf_item

class EdgeIXMetrics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @app_commands.command(name="metrics", description="Display current aggregate metrics for the EdgeIX Fabric")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    async def metrics(self, interaction: discord.Interaction) -> discord.Embed:
        """
        !!! Check RS stats for ASN !!!
        """
        aggregate_img = "https://ixp.edgeix.net.au/grapher/ixp?period=day&type=png&category=bits&protocol=all&id=1"
        #aggregate_img = "https://metrics.edgeix.net.au/render/d-solo/JmTAkICZz/edgeix-aggregates?orgId=2&panelId=9&from=now-24h&to=now"
        async with self.session.get("https://ixp.edgeix.net.au/grapher/ixp?period=day&type=json&category=bits&protocol=all&id=1", timeout=10) as resp:
            data = await resp.json()
        
        stats = data.get("statistics")

        cur_in = round(stats.get("curin") / 1000000000, 2)
        cur_out = round(stats.get("curout") / 1000000000, 2)

        embed = discord.Embed(
            title = "EdgeIX Aggregates",
            url = "https://edgeix.net",
            color = discord.Color.orange()
        )
        embed.set_author(name="EdgeIX Bot", url="https://edgeix.net", icon_url="https://i.imgur.com/63RePV2.png")
        embed.add_field(name="Current In", value=f"{cur_in}Gbps", inline=True)
        embed.add_field(name="Current Out", value=f"{cur_out}Gbps", inline=True)
        embed.set_image(url=aggregate_img)

        await interaction.response.send_message(embed=embed, ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(EdgeIXMetrics(bot))
