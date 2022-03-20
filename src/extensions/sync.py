#!/usr/bin/env python3
import asyncio
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from utils.functions import format_message

class CommandSync(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin-sync", description="Sync commands to guild")
    @app_commands.guilds(discord.Object(id=315675857639178251))
    async def admin_sync(self, interaction: discord.Interaction) -> discord.Embed:
        """
        """
        await self.bot.tree.sync(guild=discord.Object(id=315675857639178251))
        embed = await format_message(
            "Success",
            "Commands have been synced",
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(CommandSync(bot))
