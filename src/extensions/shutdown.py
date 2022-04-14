#!/usr/bin/env python3
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from utils.decorators import has_permissions
from utils.permissions import GLOBAL_ADMIN_PERMISSION
from utils.config import get_conf_item

class GracefulShut(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gshut", description="Graceful shutdown of the bot")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    @app_commands.checks.has_any_role(*GLOBAL_ADMIN_PERMISSION)
    async def graceful_shut(self, interaction: discord.Interaction):
        await self.bot.close()

    @graceful_shut.error
    async def graceful_shut_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You are not authorised to run this command!", ephemeral=True)
            return

        raise error

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(GracefulShut(bot))
