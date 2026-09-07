#!/usr/bin/env python3
import asyncio

import discord
from discord.ext import commands, tasks

from rich.console import Console
from utils.functions import HTTPRequestError, InvalidResponseError, fetch_json


class RouteServerLoop(commands.Cog):
    """
        Loop Route servers every x interval to collect state data
    """
    def __init__(self, bot):
        self.bot = bot
        self.route_server_data = self.bot.config["ROUTE_SERVERS"]
        self.console = Console()
        self.get_route_server_data.start()

    @tasks.loop(minutes=3)
    async def get_route_server_data(self):
        for loc, loc_data in self.route_server_data.items():
            for rs, rsd in loc_data.items():
                previous_data = dict(rsd.get("data") or {})
                successful = True
                for protocol in ["ipv4", "ipv6"]:
                    url = rsd.get("url")
                    if not url:
                        successful = False
                        continue
                    try:
                        endpoint = url.format(protocol=protocol)
                        data = await fetch_json(self.bot.session, endpoint)
                        protocols = data.get("protocols")
                        if not isinstance(protocols, dict) or any(
                            not isinstance(entry, dict) for entry in protocols.values()
                        ):
                            raise InvalidResponseError(
                                f"HTTP GET to {endpoint} returned invalid route-server schema"
                            )
                        previous_data[protocol] = data
                    except (HTTPRequestError, KeyError, TypeError, ValueError) as exc:
                        successful = False
                        self.console.print(f"[red]{exc}[/]")

                if previous_data:
                    rsd["data"] = previous_data
                if successful and len(previous_data) == 2:
                    rsd.pop("error", None)
                else:
                    rsd["error"] = True

        self.bot.rs.data = self.route_server_data
    
    @get_route_server_data.before_loop
    async def before_get_route_server_data(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.get_route_server_data.cancel()

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(RouteServerLoop(bot))
