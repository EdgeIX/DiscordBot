#!/usr/bin/env python3
import asyncio
import aiohttp
from typing import Optional

from rich.console import Console

import discord
from discord.ext import commands, tasks

class BGPToolkitAPI(commands.Cog):
    """
        Python Wrapper for bgptoolkit.net
    """
    def __init__(self):
        self.console = Console()

    async def get_asn_name(self, asn):
        """ 
        Get ASN name from BGP Toolkit API

        Arguments:
            asn (int): ASN to obtain

        Return:
            dict: JSON blop from bgptoolkit.net
        """
        session = aiohttp.ClientSession()
        url = f"https://bgptoolkit.net/api/asn/{asn}"

        async with session.get(url=url) as resp:
            if resp.status == 200:
                data = await resp.json()
                try:
                    return data["data"].get("name")
                except Exception as e:
                    return "UNKNOWN"
            else:
                self.console.print(f"[red]HTTP GET to {url} returned non 200 response[/]")
                return {}
    