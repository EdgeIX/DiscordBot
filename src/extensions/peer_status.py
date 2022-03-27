#!/usr/bin/env python3
import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from utils.functions import format_message
from utils.constants import ASN_REGEX
from utils.config import get_conf_item

class PeerStatus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="peer", description="test")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    #@commands.has_any_role(*GLOBAL_ADMIN_PERMISSION)
    async def peer_status(self, interaction: discord.Interaction, asn: int) -> discord.Embed:
        """
        """
        match = ASN_REGEX.match(str(asn))
        if match:
            response, header = self.bot.rs.on_message(asn)
            embed = await format_message(
                f"Peer Status for AS{asn}",
                response,
            )
        else:
            embed = await format_message(
                "Error",
                "Please enter a valid ASN!",
                "Response"
            )
        await interaction.response.send_message(embed=embed, ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(PeerStatus(bot))
