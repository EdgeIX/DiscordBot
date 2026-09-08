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

class PeerInformation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="peer", description="Get peer information for an ASN")
    @app_commands.describe(asn="Autonomous System Number")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    async def whois(self, interaction: discord.Interaction, asn: int) -> discord.Embed:
        """
        """
        await interaction.response.defer()
        data = self.bot.ixp.get_asn_data(asn)
        if not data:
            embed = await format_message(
            "404 - Not Found!",
            f"AS{asn} is unknown to EdgeIX!\n\nQuick Links:\nhttps://bgptoolkit.net/api/asn/{asn}\nhttps://bgp.he.net/AS{asn}\nhttps://www.peeringdb.com/asn/{asn}",
            f"Perhaps AS{asn} should reach out to peering@edgeix.net?"
            )
            await interaction.followup.send(embed=embed, ephemeral=False)
        else:
            embed = await self.format_data(data)
            await interaction.followup.send(embed=embed, ephemeral=False)

    async def format_data(self, data: dict):
        """

        """
        embed = discord.Embed(
            title = f"Peer Information for {data['name']}",
            url = "https://edgeix.net",
            color = discord.Color.orange()
        )
        embed.set_author(name="EdgeIX Bot", url="https://edgeix.net", icon_url="https://i.imgur.com/63RePV2.png")
        embed.add_field(name="ASN", value=data["asnum"], inline=True)
        embed.add_field(name="Member Since", value=data["member_since"], inline=True)
        embed.add_field(name="Peering Policy", value=data["peering_policy"], inline=True)
        
        table = PrettyTable()
        table.field_names = ["Peering Fabric", "IPv4", "IPv6"]
        route_server_enabled = []
        for connection in data.get("connection_list") or []:
            ixp_id = connection.get("ixp_id", "unknown")
            ixp = self.bot.ixp.ixp_id.get(ixp_id, {})
            vlan = (connection.get("vlan_list") or [{}])[0]
            v4 = vlan.get("ipv4") or {}
            v6 = vlan.get("ipv6")
            v4_address = v4.get("address")
            v4_state = self.bot.rs.get_session_from_ip(v4_address) if v4_address else None
            route_server_enabled.append(bool(v4_state and v4_state.get("state") == "up"))
            if not v6:
                table.add_row([
                    ixp.get("name", ixp_id),
                    v4_address or "N/A",
                    "N/A",
                ])
            else:
                v6_address = v6.get("address")
                v6_state = self.bot.rs.get_session_from_ip(v6_address) if v6_address else None
                route_server_enabled.append(bool(v6_state and v6_state.get("state") == "up"))
                table.add_row([
                    ixp.get("name", ixp_id),
                    v4_address or "N/A",
                    v6_address or "N/A",
                ])
        
        # Perform logic to work out ASNs route server presence
        if route_server_enabled and all(route_server_enabled):
            route_servers = "Present"
        elif any(route_server_enabled):
            route_servers = "Selective"
        else:
            route_servers = "Not Present"
        
        embed.add_field(name="Route Servers", value=route_servers, inline=True)

        try:
            embed.add_field(name="Contact", value=data["contact_email"][0], inline=True)
        except (IndexError, KeyError, TypeError):
            pass

        embed.add_field(name="Peering Locations", value=f"```{table}```", inline=False)

        return embed


async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(PeerInformation(bot))
