#!/usr/bin/env python3
import asyncio
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from utils.functions import format_message
from utils.decorators import has_permissions
from utils.permissions import GLOBAL_ADMIN_PERMISSION
from utils.config import get_conf_item

class CommandSync(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin-sync", description="Sync commands to guild")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    @app_commands.checks.has_any_role(*GLOBAL_ADMIN_PERMISSION)
    async def admin_sync(self, interaction: discord.Interaction) -> discord.Embed:
        """
        Sync commands in the bot command tree to current discord guild
        """
        await self.bot.tree.sync(guild=discord.Object(id=get_conf_item("GUILD_ID")))
        embed = await format_message(
            "Success",
            "Commands have been synced",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @admin_sync.error
    async def admin_sync_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You are not authorised to run this command!", ephemeral=True)
            return

        raise error

    @commands.command(name="admin-sync-legacy")
    async def admin_sync_legacy(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        await self.bot.tree.sync(guild=discord.Object(id=get_conf_item("GUILD_ID")))

async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(CommandSync(bot))
