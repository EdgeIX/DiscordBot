#!/usr/bin/env python3
import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from utils.functions import format_message
from utils.constants import ASN_REGEX
from utils.config import get_conf_item
from utils.enums import PeeringLocations

class WhoIsPeering(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="whois-peering", description="Who is Peering on a given fabric")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    async def whois_peering(self, interaction: discord.Interaction, location: PeeringLocations) -> discord.Embed:
        """
        Check what ASNs are peering at a given location.

        Logic needed to be applied within this function to get around
        the 1024 byte limit in the Discord.py Embed function

        Arguments:
            interaction (discord.Interaction): Interaction object passed from app_commands
            location (PeeringLocations): Enum object derived from PeeringLocations Enum definition
        
        Example:
            /whois_peering Brisbane
        """
        await interaction.response.defer()
        response = self.bot.rs.peers_by_location(location.value) or []
        total = len(response)
        if not response:
            embed = await format_message(
                "Who is Peering?",
                "No peers found at this location.",
                None,
                f"Peers for {location.name} (Total: 0)",
            )
            await interaction.followup.send(embed=embed, ephemeral=False)
            return

        chunks = []
        current = []
        current_length = 0
        for peer in response:
            line = str(peer)
            if len(line) > 1024:
                line = f"{line[:1021]}..."
            line_length = len(line) + (1 if current else 0)
            if current and current_length + line_length > 1024:
                chunks.append("\n".join(current))
                current = []
                current_length = 0
            current.append(line)
            current_length += len(line) + (1 if len(current) > 1 else 0)
        if current:
            chunks.append("\n".join(current))

        for index, chunk in enumerate(chunks):
            header = f"Peers for {location.name} (Total: {total})" if index == 0 else f"Peers for {location.name} Cont. (Total: {total})"
            embed = await format_message("Who is Peering?", chunk, None, header)
            await interaction.followup.send(embed=embed, ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(WhoIsPeering(bot))
