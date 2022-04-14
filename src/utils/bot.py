#!/usr/bin/env python3
import asyncio
import datetime
import os
from operator import attrgetter
from typing import Generator, List, Union

import aiohttp
import discord
from discord.ext import commands

from utils.classes import NoneClass
from utils.errors import print_error
from utils.route_server import RouteServerInteraction
from utils.config import ProjectConfig
from utils.bgp import BGPToolkitAPI
from utils.ixp import IXPManager


__all__ = ("EdgeIXBot", "EdgeIXBotContext")

class EdgeIXBot(commands.Bot):
    """A subclass of commands.Bot."""

    def __init__(self, *, specified_loop=None):
        """Makes a instance of WMBot."""
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
        loop = asyncio.get_event_loop()
        session = aiohttp.ClientSession(loop=loop)

        # Load all the environment variables
        #load_dotenv("config/Bot/token.env")
        #load_dotenv("config/Apis/tokens.env")
        #load_dotenv("config/Database/db.env")

        # We save the bot start time to a variable
        self.started_at = datetime.datetime.utcnow()

        # For api requests
        self.session = session

        # For config items
        self.config = ProjectConfig().c

        # Route Server interaction
        self.rs = RouteServerInteraction(self)

        # IXP Manager Interaction
        self.ixp = IXPManager()

        # For BGP Toolkit interaction
        self.bgptoolkit = BGPToolkitAPI()

        super().__init__(
            command_prefix="!",
            case_insensitive=True,
            intents=intents,
            session=session,
            loop=specified_loop or loop,
            strip_after_prefix=True,
        )

        # For before_invoke
        self._before_invoke = self.before_invoke

    async def get_context(self, message: discord.Message, *, cls: commands.Context = None) -> commands.Context:
        """Return the custom context."""
        return await super().get_context(message, cls=cls or EdgeIXBotContext)

    async def close(self):
        await self.session.close()
        await super().close()

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
        req = await self.session.post("https://hastebin.com/documents", data=text)
        reqjson = None
        try:
            reqjson = await req.json()
            key = reqjson["key"]
        except (TypeError, KeyError, aiohttp.ContentTypeError):
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
        await ctx.channel.trigger_typing()


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
                # We check if the content was in a codeblock
                cb = await CodeblockConverter().convert(self, args[0])
                if cb is None:
                    # If it's not in a codeblock, we just make a url normally
                    url = await self.bot.hastebin_upload(args[0])
                else:
                    # If it's in a codeblock, we make a url with the code language for syntax highlighting
                    url = await self.bot.hastebin_upload(cb.content)
                    url = url + "." + cb.language
                message = await self.send(
                    embed=discord.Embed(title="Content too long", description=f"Uploaded to cloud: {url}")
                )
            else:
                raise error
        except Exception as error:
            raise error
        
        return message