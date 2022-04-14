#!/usr/bin/env python3
import os
import logging
import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import track

from utils.bot import EdgeIXBot


blacklisted_extensions = ["__init__.py"]
initial_extensions = []

bot = EdgeIXBot()
console = Console()
logging.basicConfig(level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])

def build_extensions():
    for file in os.listdir(bot.config.c["EXTENSIONS_DIR"]):
        if file.endswith(".py") and not file in blacklisted_extensions:
            initial_extensions.append("extensions." + file[:-3])
    
    for file in os.listdir(bot.config.c["TASKS_DIR"]):
        if file.endswith(".py") and not file in blacklisted_extensions:
            initial_extensions.append("tasks." + file[:-3])

    for file in os.listdir(bot.config.c["EVENTS_DIR"]):
        if file.endswith(".py") and not file in blacklisted_extensions:
            initial_extensions.append("events." + file[:-3])

    #for file in os.listdir(bot.config.c["MENUS_DIR"]):
    #    if file.endswith(".py") and not file in blacklisted_extensions:
    #        initial_extensions.append("menus." + file[:-3])

async def on_ready():
    """
        Run on bot Startup
    """
    # We use this so that this event only fires after the bot is ready
    await bot.wait_until_ready()

    console.print("[green]Bot is online[/]")

    # We load our hot reloading cog. This will reload cogs as we edit them in real time
    await bot.load_extension("hotreload")

    # We loop through all the extensions and load them.
    # If there is a error we print it to the console and add the cog name to unloaded
    unloaded = []
    for extension in track(initial_extensions, description="[yellow]Loading Cogs[/]"):
        try:
            await bot.load_extension(extension)
        except commands.ExtensionFailed as exc:
            unloaded.append(extension.split(".")[-1])
            console.print_exception()

    # If there are errors, then we send a message to the user notifying them
    if unloaded:
        console.print(
            f"Couldn't load {len(unloaded)}/{len(initial_extensions)} cogs ({', '.join(unloaded)}). Check the console for details."
        )

    console.print("[green]Bot ready[/]")

    console.print("[green]All cogs loaded[/]")

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for more potential peers.."))

@bot.event
async def on_command_errror(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        console.print("[red]Error: ({error.status} {error.code}: {error.text})[/]")

async def main():
    async with bot:
        bot.loop.create_task(on_ready())
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
    build_extensions()
    asyncio.run(main())
