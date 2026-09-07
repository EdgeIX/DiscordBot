#!/usr/bin/env python3
import asyncio
from typing import Optional

import discord
from discord.ext import commands, tasks

from utils.functions import format_message

class GoodbyeFromEdgeIX(commands.Cog):
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
    async def on_member_remove(self, member: discord.Member):
        """
        Handle user leave events

        Arguments:
            member (discord.Member): Payload containing member information
        """
        guild = member.guild
        # TODO: make a better bye bye message.
        message = f"Bye bye {member.mention}"
        embed = await format_message("Please don't Go!", message)
        channel = await self._get_channel()
        await channel.send(embed=embed)

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(GoodbyeFromEdgeIX(bot))
