#!/usr/bin/env python3
import logging
import asyncio

import discord
from discord.ext import commands
from rich.console import Console
from rich.logging import RichHandler

from utils.bot import EdgeIXBot


bot = EdgeIXBot()
console = Console()
logging.basicConfig(level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])

@bot.event
async def on_ready():
    """
        Run on bot Startup
    """
    console.print("[green]Bot is online[/]")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for more potential peers.."))

@bot.event
async def on_command_errror(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        console.print("[red]Error: ({error.status} {error.code}: {error.text})[/]")

async def main():
    async with bot:
        try:
            await bot.start(bot.config["TOKEN"])
        except KeyboardInterrupt:
            console.print("[red]Bot Closing[/]")
        except discord.PrivilegedIntentsRequired:
            console.print(
                "[red]Go to [/][blue]https://discord.com/developers/applications/[/][red] and enable the intents that are required. Currently these are as follows:[/]"
            )
        except discord.LoginFailure:
            console.print("[red]The token is most likely incorrect[/]")
        except discord.ConnectionClosed as e:
            console.print(f"[red]Connection closed[/][yellow]Code: {e.code} Reason: {e.reason}[/]")
        except discord.HTTPException as e:
            console.print("[red]Could not connect to discord.com ({e.status} {e.code}: {e.text})[/]")
        except KeyError:
            console.print("[red]No token found in the environment variables[/]")
        except discord.GatewayNotFound:
            console.print("[red]The API is probably having an outage,[/] [blue]see https://discordstatus.com[/]")
        except Exception as e:
            raise e

if __name__ == "__main__":
    asyncio.run(main())
