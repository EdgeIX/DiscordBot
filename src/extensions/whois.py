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
        pass

async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(WhoIs(bot))
