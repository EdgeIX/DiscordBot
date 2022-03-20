#!/usr/bin/env python3
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

class GracefulShut(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gshut", description="Graceful shutdown of the bot")
    @app_commands.guilds(discord.Object(id=315675857639178251))
    async def graceful_shut(self, interaction: discord.Interaction):
        await self.bot.close()

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(GracefulShut(bot))
