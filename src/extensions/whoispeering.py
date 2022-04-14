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
        response = self.bot.rs.peers_by_location(location.value)
        total = len(response)
        peers_modified = response[:]

        first = True

        while len(peers_modified) != 0:

            char_counter = 0
            can_send = []

            while char_counter < 1024:
                # As we iterate a different list we need to set the original peers
                # to be a copy of the modified list after the character limit is hit
                # and while loop is broke. Failure to do this would result in an IndexError
                # when attempting to pop 
                peers = peers_modified[:]
                for peer in peers:
                    # count new line chars too
                    char_counter += len(f"{peer}\n")
                    if char_counter > 1024: break
                    can_send.append(peer)
                    peers_modified.pop(0)
                break

            header = f"Peers for {location.name} (Total: {total})" if first \
                        else f"Peers for {location.name} Cont. (Total: {total})"

            response = "\n".join(can_send)
            embed = await format_message(
                "Who is Peering?",
                response,
                None,
                header,
            )

            if first:
                await interaction.response.send_message(embed=embed, ephemeral=False)
                first = False
            else:
                await interaction.followup.send(embed=embed, ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(WhoIsPeering(bot))
