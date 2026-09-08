#!/usr/bin/env python3
from rich.console import Console
from discord.ext import commands, tasks
from utils.functions import HTTPRequestError, InvalidResponseError, fetch_json

class ValidPeerLoop(commands.Cog):
    """
        Loop IXPM API every X interval to load peer data into
        runtime memory
    """
    def __init__(self, bot):
        self.bot = bot
        self.console = Console()
        self.headers = {
            "X-IXP-Manager-API-Key": self.bot.config["IXPM_API_KEY"]
        }
        self.get_valid_peers.start()

    @tasks.loop(minutes=10)
    async def get_valid_peers(self):
        asns = {}
        try:
            data = await fetch_json(
                self.bot.session,
                self.bot.config["IXPM_PEER_INFO"],
                headers=self.headers,
                ssl=self.bot.config.get("IXPM_VERIFY_SSL", True),
            )
            member_list = data.get("member_list")
            ixp_list = data.get("ixp_list")
            if not isinstance(member_list, list) or not isinstance(ixp_list, list):
                raise InvalidResponseError("IXPM peer refresh returned invalid schema")
            ixp_id = {}
            for ixp in ixp_list:
                if not isinstance(ixp, dict) or "ixp_id" not in ixp:
                    raise InvalidResponseError("IXPM peer refresh returned invalid IXP schema")
                try:
                    hash(ixp["ixp_id"])
                except (KeyError, TypeError):
                    raise InvalidResponseError("IXPM peer refresh returned invalid IXP schema")
                ixp_id[ixp["ixp_id"]] = {"name": ixp.get("shortname", str(ixp["ixp_id"]))}
        except HTTPRequestError as exc:
            self.console.print(f"[red]{exc}[/]")
            return

        for peer in member_list:
            try:
                asns[int(peer["asnum"])] = peer["name"]
            except (KeyError, TypeError, ValueError):
                self.console.print("[red]IXPM peer refresh returned invalid member schema[/]")
                return
        self.bot.ixp.data = data
        self.bot.ixp.asns = asns
        self.bot.ixp.ixp_id = ixp_id
    
    @get_valid_peers.before_loop
    async def before_get_valid_peers(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.get_valid_peers.cancel()

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(ValidPeerLoop(bot))
