#!/usr/bin/env python3
import asyncio
import aiohttp
from typing import Optional

import discord
from discord.ext import commands, tasks

class ValidPeerLoop(commands.Cog):
    """
        Loop IXPM API every X interval to load peer data into
        runtime memory
    """
    def __init__(self, bot):
        self.bot = bot
        #self.session = aiohttp.ClientSession()
        self.headers = {
            "X-IXP-Manager-API-Key": self.bot.config["IXPM_API_KEY"]
        }
        self.get_valid_peers.start()

    @tasks.loop(minutes=10)
    async def get_valid_peers(self):
        asns = {}
        session = aiohttp.ClientSession()
        async with session.get(headers=self.headers, url=self.bot.config["IXPM_PEER_INFO"]) as resp:
            if resp.status == 200:
                self.bot.ixp.data = await resp.json()
                for peer in self.bot.ixp.data["member_list"]:
                    asns.update({int(peer["asnum"]): peer["name"]})
                self.bot.ixp.asns = asns
                # Update IXP ID dict
                self.bot.ixp.make_ixp_dict()
        await session.close()
    
    @get_valid_peers.before_loop
    async def before_get_valid_peers(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(ValidPeerLoop(bot))
