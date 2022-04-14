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
        data = self.bot.ixp.get_asn_data(asn)
        if not data:
            embed = await format_message(
            "404 - Not Found!",
            f"AS{asn} is unknown to EdgeIX!\n\nQuick Links:\nhttps://bgptoolkit.net/api/asn/{asn}\nhttps://bgp.he.net/AS{asn}\nhttps://www.peeringdb.com/asn/{asn}",
            f"Perhaps AS{asn} should reach out to peering@edgeix.net?"
            )
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            embed = await self.format_data(data)
            await interaction.response.send_message(embed=embed, ephemeral=False)

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
        for connection in data["connection_list"]:
            ixp = self.bot.ixp.ixp_id.get(connection["ixp_id"])
            v4 = connection["vlan_list"][0].get("ipv4")
            v6 = connection["vlan_list"][0].get("ipv6")
            #route_server_enabled.append(v4.get("routeserver"))
            v4_state = self.bot.rs.get_session_from_ip(v4.get("address"))
            route_server_enabled.append(True) if v4_state.get("state") == "up" else route_server_enabled.append(False)
            if v6 is None:
                table.add_row([
                    ixp["name"],
                    v4.get("address"),
                    "N/A",
                ])
            else:
                #route_server_enabled.append(v6.get("routeserver"))
                v6_state = self.bot.rs.get_session_from_ip(v6.get("address"))
                print(v6_state)
                route_server_enabled.append(True) if v6_state.get("state") == "up" else route_server_enabled.append(False)
                table.add_row([
                    ixp["name"],
                    v4.get("address"),
                    v6.get("address"),
                ])
        
        # Perform logic to work out ASNs route server presence
        if all(route_server_enabled):
            route_servers = "Present"
        elif any(route_server_enabled):
            route_servers = "Selective"
        else:
            route_servers = "Not Present"
        
        embed.add_field(name="Route Servers", value=route_servers, inline=True)

        try:
            embed.add_field(name="Contact", value=data["contact_email"][0], inline=True)
        except Exception as e:
            pass

        embed.add_field(name="Peering Locations", value=f"```{table}```", inline=False)

        return embed


async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(PeerInformation(bot))
