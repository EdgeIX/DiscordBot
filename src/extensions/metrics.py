#!/usr/bin/env python3
import asyncio
import logging
import time

import discord
from discord import app_commands
from discord.ext import commands

from utils.functions import format_message
from utils.constants import ASN_REGEX
from utils.config import get_conf_item
from utils.functions import HTTPRequestError, InvalidResponseError, fetch_json

class EdgeIXMetrics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="metrics", description="Display current aggregate metrics for the EdgeIX Fabric")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    async def metrics(self, interaction: discord.Interaction) -> discord.Embed:
        """
        !!! Check RS stats for ASN !!!
        """
        aggregate_img = "https://ixp.edgeix.net.au/grapher/ixp?period=day&type=png&category=bits&protocol=all&id=1"
        #aggregate_img = "https://metrics.edgeix.net.au/render/d-solo/JmTAkICZz/edgeix-aggregates?orgId=2&panelId=9&from=now-24h&to=now"
        await interaction.response.defer()
        try:
            data = await fetch_json(
                self.bot.session,
                "https://ixp.edgeix.net.au/grapher/ixp?period=day&type=json&category=bits&protocol=all&id=1",
            )
            stats = data.get("statistics")
            if not isinstance(stats, dict):
                raise InvalidResponseError("Metrics response missing statistics")
            cur_in = round(float(stats["curin"]) / 1000000000, 2)
            cur_out = round(float(stats["curout"]) / 1000000000, 2)
        except (HTTPRequestError, KeyError, TypeError, ValueError) as exc:
            logging.getLogger(__name__).warning("Metrics request failed: %s", exc)
            await interaction.followup.send("Metrics are temporarily unavailable.", ephemeral=True)
            return


        embed = discord.Embed(
            title = "EdgeIX Aggregates",
            url = "https://edgeix.net",
            color = discord.Color.orange()
        )
        embed.set_author(name="EdgeIX Bot", url="https://edgeix.net", icon_url="https://i.imgur.com/63RePV2.png")
        embed.add_field(name="Current In", value=f"{cur_in}Gbps", inline=True)
        embed.add_field(name="Current Out", value=f"{cur_out}Gbps", inline=True)
        embed.set_image(url=aggregate_img + f"&fuckcache={time.time()}")

        await interaction.followup.send(embed=embed, ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(EdgeIXMetrics(bot))
