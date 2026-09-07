#!/usr/bin/env python3
import datetime
import asyncio
import logging
from pathlib import Path
from typing import Union

import aiohttp
import discord
from discord.ext import commands

from utils.route_server import RouteServerInteraction
from utils.config import ProjectConfig
from utils.bgp import BGPToolkitAPI
from utils.ixp import IXPManager
from utils.functions import HTTPRequestError


__all__ = ("EdgeIXBot", "EdgeIXBotContext")

class EdgeIXBot(commands.Bot):
    """A subclass of commands.Bot."""

    def __init__(self):
        """Create the bot instance and its shared runtime state."""
        intents = discord.Intents(
            members=True,
            presences=True,
            guilds=True,
            emojis=True,
            invites=True,
            reactions=True,
            voice_states=True,
            messages=True,
            message_content=True,
        )

        # We save the bot start time to a variable
        self.started_at = datetime.datetime.now(datetime.timezone.utc)

        # Shared aiohttp session is created during setup_hook.
        self.session = None

        # For config items
        self.config = ProjectConfig().c

        # Route Server interaction
        self.rs = RouteServerInteraction(self)

        # IXP Manager Interaction
        self.ixp = IXPManager(self.config)

        # For BGP Toolkit interaction
        self.bgptoolkit = BGPToolkitAPI()
        self._setup_complete = False
        self._closing = False
        self.failed_extensions = []

        super().__init__(
            command_prefix="!",
            case_insensitive=True,
            intents=intents,
            strip_after_prefix=True,
        )

        # For before_invoke
        self._before_invoke = self.before_invoke

    async def setup_hook(self) -> None:
        if self._setup_complete:
            return
        timeout = aiohttp.ClientTimeout(total=15)
        self.session = aiohttp.ClientSession(timeout=timeout)
        self.bgptoolkit = BGPToolkitAPI(self.session)

        extensions = self._discover_extensions()
        for extension in extensions:
            try:
                await self.load_extension(extension)
            except commands.ExtensionError:
                logging.getLogger(__name__).exception("Could not load extension %s", extension)
                self.failed_extensions.append(extension)

        if self.config.get("ENABLE_HOT_RELOAD", False):
            try:
                await self.load_extension("hotreload")
            except commands.ExtensionError:
                logging.getLogger(__name__).exception("Could not load extension hotreload")
                self.failed_extensions.append("hotreload")

        await self.tree.sync(guild=discord.Object(id=self.config["GUILD_ID"]))
        self._setup_complete = True

    def _discover_extensions(self) -> list[str]:
        """Return active extension modules in deterministic load order."""

        modules = []
        for setting, package in (
            ("EXTENSIONS_DIR", "extensions"),
            ("TASKS_DIR", "tasks"),
            ("EVENTS_DIR", "events"),
        ):
            directory = Path(self.config[setting])
            if not directory.is_dir():
                continue
            modules.extend(
                f"{package}.{path.stem}"
                for path in sorted(directory.glob("*.py"))
                if path.stem != "__init__"
            )
        return modules

    async def get_context(self, message: discord.Message, *, cls: commands.Context = None) -> commands.Context:
        """Return the custom context."""
        return await super().get_context(message, cls=cls or EdgeIXBotContext)

    async def close(self):
        if self._closing:
            return
        self._closing = True
        try:
            # remove_cog invokes each cog's native unload hook, cancelling its
            # discord.py task loop before the client transport closes.
            for name in list(self.cogs):
                await self.remove_cog(name)
            await super().close()
        finally:
            if self.session is not None and not self.session.closed:
                await self.session.close()

    def get_user_named(self, name: str) -> Union[discord.User, None]:
        """Gets a user with the given name from the bot
        Parameters
        ----------
        name : str
            The name of the user, can have the discriminator
        Returns
        -------
        Union[discord.User, None]
            The user if it was found, otherwise None
        """
        result = None
        users = self.users

        if len(name) > 5 and name[-5] == "#":
            # The 5 length is checking to see if #0000 is in the string,
            # as a#0000 has a length of 6, the minimum for a potential
            # discriminator lookup.
            potential_discriminator = name[-4:]

            # do the actual lookup and return if found
            # if it isn't found then we'll do a full name lookup below.
            result = discord.utils.get(users, name=name[:-5], discriminator=potential_discriminator)
            if result is not None:
                return result

        def pred(user):
            return user.nick == name or user.name == name

        return discord.utils.find(pred, users)

    async def hastebin_upload(self, text: str) -> Union[str, None]:
        """Uploads the given text to hastebin
        Parameters
        ----------
        text : str
            the text to upload to hastebin
        Returns
        -------
        Union[str, None]
            The URL of the uploaded file or None if the upload failed
        """
        if self.session is None or self.session.closed:
            return None
        reqjson = None
        try:
            async with self.session.post(
                "https://hastebin.com/documents", data=text, timeout=10
            ) as response:
                if response.status < 200 or response.status >= 300:
                    raise HTTPRequestError(f"Hastebin returned HTTP {response.status}")
                reqjson = await response.json()
            key = reqjson["key"]
        except (TypeError, KeyError, ValueError, aiohttp.ContentTypeError, aiohttp.ClientError, asyncio.TimeoutError, HTTPRequestError):
            print(f"[red]Could not upload error,[/] Raw Data: {reqjson or 'Could not get raw data'}")
            url = None
        else:
            url = f"https://hastebin.com/{key}.txt"
        return url

    async def before_invoke(self, ctx):
        """
        Starts typing in the channel to let the user know that the bot received the command and is working on it.
        Parameters
        ----------
        ctx : commands.Context
            Represents the context in which a command is being invoked under.
        """
        await ctx.typing()


class EdgeIXBotContext(commands.Context):
    """A subclass of commands.Context."""

    @property
    def owner(self) -> None:
        """Call to get the owner of the bot."""
        return self.bot.get_user(self.bot.config.owner_ids[0])

    async def send(self, *args, **kwargs) -> discord.Message:
        """Sends a message
        Parameters
        ----------
        *args : tuple
            Arguments to be passed to discord.abc.Messagable.send or discord.Message.reply
        **kwargs : dict, optional
            Keyword Arguments to be passed to discord.abc.Messagable.send or discord.Message.reply
        no_reply : bool, optional
            Whether to send a reply or not, by default False
        no_cloud : bool, optional
            Whether to upload the content to cloud or not if the content is too long, by default False
        Returns
        -------
        discord.Message
            The message that was sent
        Raises
        --------
        discord.HTTPException
            Sending the message failed. If the message was too long,
            the content would be not uploaded to cloud and this
            wouldn't be raised unless the no_cloud option is set to True.
        discord.Forbidden
            You do not have the proper permissions to send the message.
        discord.InvalidArgument
            The files list is not of the appropriate size,
            you specified both file and files,
            or you specified both embed and embeds,
            or the reference object is not a discord.Message,
            discord.MessageReference or discord.PartialMessage.
        """
        if kwargs.get("no_reply") is True:
            # If the no_reply flag is set, we don't want to send a reply
            # Pop no_reply, send to super function
            kwargs.pop("no_reply", None)
            message = await super().send(*args, **kwargs)
            return message
        # Wrapping this in a try/except block because the original message can be deleted.
        # and if it is deleted then we won't be able to reply and it will raise an error
        try:
            # First we try to reply
            message = await self.reply(*args, **kwargs)
        except discord.NotFound:
            # If the original message was deleted, we just send it normally
            message = await self.send(*args, **kwargs, no_reply=True)
        except discord.HTTPException as error:
            if kwargs.get("no_upload") is True:
                # If the no_upload flag is set, we just raise the error instead of uploading
                raise error
            # If the content is too large then we send it using hastebin
            if error.status == 400 and error.code == 50035:
                if not args:
                    # If no content was passed (probably only embed was passed), we just raise the error
                    raise error
                url = await self.bot.hastebin_upload(args[0])
                message = await self.send(
                    embed=discord.Embed(title="Content too long", description=f"Uploaded to cloud: {url}")
                )
            else:
                raise error
        except Exception as error:
            raise error
        
        return message
