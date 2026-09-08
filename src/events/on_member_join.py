#!/usr/bin/env python3
import asyncio
from typing import Optional

import discord
from discord.ext import commands, tasks

from utils.functions import format_message

class WelcomeToEdgeIX(commands.Cog):
    """
        Post Hello message on user join with instructions as to how they can gain
        further permissions.
    """
    def __init__(self, bot):
        self.bot = bot

    async def _get_channel(self):
        channel_id = self.bot.config["WELCOME_CHANNEL_ID"]
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(channel_id)
        return channel

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Handle user join events

        Arguments:
            member (discord.Member): Payload containing member information
        """
        guild = member.guild
        # TODO: Change welcome message to include info about reacting
        message = f"Hello {member.mention}, Welcome to {guild.name} Discord server! If you wish, please use /addasn <myasn> to update your roles (psst.. if you are a Peer this will give you exclusive access)"
        embed = await format_message("Welcome!", message)
        channel = await self._get_channel()
        await channel.send(embed=embed)

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(WelcomeToEdgeIX(bot))
