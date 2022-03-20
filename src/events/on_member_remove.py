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
        self.channel = bot.get_channel(bot.config["WELCOME_CHANNEL_ID"])

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
        await self.channel.send(embed=embed)

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(GoodbyeFromEdgeIX(bot))
