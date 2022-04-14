#!/usr/bin/env python3
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from menus.announcements import EdgeIXAnnouncementModal
from utils.decorators import has_permissions
from utils.permissions import GLOBAL_ADMIN_PERMISSION
from utils.config import get_conf_item

class EdgeIXAnnouncements(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="announcement", description="Send an announcement with EdgeIX Branding")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    @app_commands.checks.has_any_role(*GLOBAL_ADMIN_PERMISSION)
    async def send_announcement(self, interaction: discord.Interaction) -> discord.Embed:
        await interaction.response.send_modal(EdgeIXAnnouncementModal())

    @send_announcement.error
    async def send_announcement_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You are not authorised to run this command!", ephemeral=True)
            return

        raise error

async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(EdgeIXAnnouncements(bot))
