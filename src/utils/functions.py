#!/usr/bin/env python3
import asyncio
import discord
import requests

from rich.console import Console

from discord.ext import commands


async def format_message(
    title: str,
    value: str,
    footer: str = None,
    header: str = "Response"
    ) -> discord.embeds.Embed:
    """
    Helper function to generate embedded message

    Arguments:
        title (str):  Title for the embed
        value (str): Body of the embed
        Header (str): Fucks me

    Returns:
        str: Returns discord.embeds.Embed
    """
    embed = discord.Embed(
        title = title,
        url = 'https://edgeix.net',
        color = discord.Color.orange()
    )
    embed.set_author(name='EdgeIX Bot', url='https://edgeix.net', icon_url='https://i.imgur.com/63RePV2.png')
    embed.add_field(name=header, value=value, inline=True)
    if footer:
        embed.set_footer(text=footer)
    return embed

async def json_loader(url: str):
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except Exception as e:
        console = Console()
        console.print(f"[red]HTTP GET to {url} raised {str(e)}[/]")
        return None
