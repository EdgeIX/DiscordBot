#!/usr/bin/env python3
import asyncio
import discord
import aiohttp

from rich.console import Console

from discord.ext import commands


class HTTPRequestError(RuntimeError):
    """A request failed before a usable JSON response was received."""


class HTTPStatusError(HTTPRequestError):
    """An HTTP endpoint returned a non-success status."""

    def __init__(self, url: str, status: int) -> None:
        super().__init__(f"HTTP GET to {url} returned {status}")
        self.url = url
        self.status = status


class InvalidResponseError(HTTPRequestError):
    """An endpoint returned malformed JSON or an unexpected top-level value."""


async def fetch_json(session, url: str, *, timeout: float = 10, ssl=None, headers=None) -> dict:
    """Fetch a JSON object with common timeout/status/content checks."""

    request_args = {"timeout": timeout}
    if ssl is not None:
        request_args["ssl"] = ssl
    if headers is not None:
        request_args["headers"] = headers

    try:
        async with session.get(url=url, **request_args) as response:
            if response.status < 200 or response.status >= 300:
                raise HTTPStatusError(url, response.status)
            try:
                payload = await response.json()
            except (aiohttp.ContentTypeError, ValueError) as exc:
                raise InvalidResponseError(f"HTTP GET to {url} returned invalid JSON") from exc
    except HTTPRequestError:
        raise
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        raise HTTPRequestError(f"HTTP GET to {url} failed: {exc}") from exc

    if not isinstance(payload, dict):
        raise InvalidResponseError(f"HTTP GET to {url} returned a non-object JSON value")
    return payload


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
