#!/usr/bin/env python3
import asyncio
import aiohttp

import discord
from discord.ext import commands, tasks

from rich.console import Console


class RouteServerLoop(commands.Cog):
    """
        Loop Route servers every x interval to collect state data
    """
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.route_server_data = self.bot.config["ROUTE_SERVERS"]
        self.console = Console()
        self.get_route_server_data.start()

    @tasks.loop(minutes=3)
    async def get_route_server_data(self):
        for loc, loc_data in self.route_server_data.items():
            for rs, rsd in loc_data.items():
                rsd["data"] = {}
                for protocol in ["ipv4", "ipv6"]:
                    try:
                        async with self.session.get(url=rsd.get('url').format(protocol=protocol), timeout=10) as resp:
                            data = await resp.json()
                            rsd["data"][protocol] = data
                    except Exception as e:
                        self.console.print(f"[red]HTTP GET for {rsd.get('url').format(protocol=protocol)} raised {str(e)}[/]")
                        rsd["error"] = True

        self.bot.rs.data = self.route_server_data
    
    @get_route_server_data.before_loop
    async def before_get_route_server_data(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(RouteServerLoop(bot))
