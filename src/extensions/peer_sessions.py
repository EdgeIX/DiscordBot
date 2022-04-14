#!/usr/bin/env python3
import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get

from prettytable import PrettyTable

from utils.functions import format_message
from utils.constants import ASN_REGEX
from utils.config import get_conf_item

class PeerSessions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="peer-sessions", description="Get Route Server session state for an ASN")
    @app_commands.describe(asn="ASN to query")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    async def peer_sessions(self, interaction: discord.Interaction, asn: int) -> discord.Embed:
        """
        Get Peer Session state from the Route Servers

        Arguments:
            interaction (discord.Interaction): Command utilisation, allowing response etc
            asn (int): ASN in integer format to query

        Returns:
            discord.Embed: Non ephemeral message with Peer Session state
        """
        as_match = ASN_REGEX.match(str(asn))
        if not as_match:
            embed = await format_message(
                "Error",
                f"{asn} is not a valid ASN!",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            data = self.bot.ixp.get_asn_data(asn)
            if not data:
                embed = await format_message(
                "404 - Not Found!",
                f"AS{asn} is unknown to EdgeIX!\n\nQuick Links:\nhttps://bgptoolkit.net/api/asn/{asn}\nhttps://bgp.he.net/AS{asn}\nhttps://www.peeringdb.com/asn/{asn}",
                f"Perhaps AS{asn} should reach out to peering@edgeix.net?"
                )
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                table = PrettyTable()
                table.field_names = ["ASN", "Peering Fabric", "RS v4", "RS v6"]
                for connection in data["connection_list"]:
                    ixp = self.bot.ixp.ixp_id.get(connection["ixp_id"])
                    v4 = connection["vlan_list"][0].get("ipv4")
                    v4_state = self.bot.rs.get_session_from_ip(v4.get("address"))
                    v6 = connection["vlan_list"][0].get("ipv4")
                    v6_state = self.bot.rs.get_session_from_ip(v6.get("address"))
                    if v6 is None:
                        v6 = {"routeserver": "false"}
                    table.add_row([
                        data["asnum"],
                        ixp["name"],
                        v4_state.get("state"),
                        v6_state.get("state"),
                    ])
                embed = await format_message(
                data.get("name"),
                f"```{table}```",
                None,
                "Peering in the following locations:"
                )
                await interaction.response.send_message(embed=embed, ephemeral=False)



async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(PeerSessions(bot))
