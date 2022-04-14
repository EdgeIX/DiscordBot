#!/usr/bin/env python3
import asyncio
from typing import Optional

import discord
from discord.ext import commands, tasks

from utils.functions import format_message

class WaitForDM(commands.Cog):
    """
        Event Listener used to bounce messages sent to the bot
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Handle DMs to the bot

        Arguments:
            message (discord.Message): Payload containing message information
        """
        # Dont loop responding to our own message
        if message.author == self.bot.user:
            return
        
        if not message.guild:
            embed = await format_message("Beep Boop I am a bot", "I am a bot and do not respond to DMs! Please use the EdgeIX Discord for communication.")
            await message.channel.send(embed=embed)

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(WaitForDM(bot))
