#!/usr/bin/env python3
import asyncio
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from utils.functions import format_message
from utils.constants import ASN_REGEX

from menus.asn_approval import ApprovalMenuView

class AddASN(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel = bot.get_channel(bot.config["ROLE_APPROVAL_CHANNEL_ID"])

    @app_commands.command(name="addasn", description="Add an ASN role to yourself!")
    @app_commands.guilds(discord.Object(id=315675857639178251))
    async def add_asn(self, interaction: discord.Interaction, asn: int) -> discord.Embed:
        """
        """
        member = interaction.user
        user_message = await format_message("ASN Approval", f"Hi {member.name}, your request to add yourself to AS{asn} has been queued for approval")
        staff_message = await format_message("ASN Approval", f"{member.name} wishes to add themselves to AS{asn}, please action this approval.")

        message_id = await interaction.response.send_message(embed=user_message)
        await self.channel.send(view=ApprovalMenuView(member, asn, interaction),embed=staff_message)

        #await interaction.response.send_message(embed=embed, ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(AddASN(bot))
