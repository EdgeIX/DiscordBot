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
from utils.enums import WhoisTypes

class WhoIs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel = bot.get_channel(bot.config["ROLE_APPROVAL_CHANNEL_ID"])

    @app_commands.command(name="whois", description="Whois an IP/ASN Object, find out if they're on EdgeIX!")
    @app_commands.describe(query="IP/ASN Object to query")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    async def whois(self, interaction: discord.Interaction, query_type: WhoisTypes, query: str) -> discord.Embed:
        """
        !!!!!! PROBABLY NOT REALLY WHOIS?? MAYBE MOVE TO /PEER-INFO??? !!!!!!
        """
        if query_type == WhoisTypes.ASN:
            as_match = ASN_REGEX.match(query)
            if not as_match:
                embed = await format_message(
                    "Error",
                    f"{query} is not a valid ASN!",
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                data = self.bot.ixp.get_asn_data(int(query))
                if not data:
                    embed = await format_message(
                    "Error",
                    f"AS{query} is unknown to EdgeIX!\nQuick Links:\nhttps://bgptoolkit.net/api/asn/{message}\nhttps://bgp.he.net/AS{message}",
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=False)
                else:
                    table = PrettyTable()
                    table.field_names = ["ASN", "Peering Fabric", "RS v4", "RS v6"]
                    for connection in data["connection_list"]:
                        ixp = self.bot.ixp.ixp_id.get(connection["ixp_id"])
                        v4 = connection["vlan_list"][0].get("ipv4")
                        v6 = connection["vlan_list"][0].get("ipv4")
                        if v6 is None:
                            v6 = {"routeserver": "false"}
                        table.add_row([
                            data["asnum"],
                            ixp["name"],
                            v4.get("routeserver"),
                            v6.get("routeserver"),
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
    await bot.add_cog(WhoIs(bot))
