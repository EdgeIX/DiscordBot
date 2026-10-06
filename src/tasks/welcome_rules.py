#!/usr/bin/env python3
import asyncio
import logging
from typing import Optional

import discord
from discord.ext import commands, tasks

from utils.functions import format_message

ACCEPT_EMOJI = "\U00002705"
log = logging.getLogger(__name__)

class EdgeIXRules(commands.Cog):
    """
        Post rules to a channel to allow users to interact to gain
        further role privileges
    """
    def __init__(self, bot):
        self.bot = bot
        self.channel = None

        self.send_welcome.start()
    
    @tasks.loop(count=1)
    async def send_welcome(self):
        if self.channel is None:
            self.channel = self.bot.get_channel(self.bot.config["RULES_CHANNEL_ID"])
            if self.channel is None:
                self.channel = await self.bot.fetch_channel(self.bot.config["RULES_CHANNEL_ID"])
        if self.channel is None:
            return
        # Delete old message

        rules = [
            "This server is open to all industry professionals who are interested in or involved with peering. Your conduct is on display, so please treat this space with professionalism!",
            "\n**If you are an EdgeIX peer,** you will need to register your Discord account against your ASN to receive 'Peer' access, which gives you the ability to talk in our private peering channels. This can be done by typing **/addasn <asn>** in any channel. If you are not a peer, your account will be provided with access to our Public discussion channels only.",
            "\nBy joining this server you agree to the Discord Terms (https://discord.com/terms) and Guidelines (https://discord.com/guidelines).",
            "\nPlease click the ✅ to indicate your acceptance and enter the server.",
        ]
        embed = await format_message(
            "Welcome to the EdgeIX Discord server!",
            "\n".join(rules),
            None,
            "Overview"
        )

        # Delete all existing messages, modify bot rules if a message is present
        # to prevent spamming the channel with a ping every time the bot is started
        messages = self.channel.history()
        message_modified = False

        async for message in messages:
            if message.author.id == self.bot.user.id and not message_modified:
                await message.edit(embed=embed)
                self.bot.rules_msg = message
                message_modified = True
            else:
                await message.delete()
        
        if not message_modified:
            self.bot.rules_msg = await self.channel.send(embed=embed)

        await self.bot.rules_msg.add_reaction(ACCEPT_EMOJI)
        await self.sweep_pending_acceptances(self.bot.rules_msg)

    async def sweep_pending_acceptances(self, message: discord.Message):
        """
        Grant the role to anyone whose acceptance reaction was left unprocessed,
        e.g. reactions added while the bot was offline or the listener was failing
        """
        reaction = discord.utils.find(lambda r: str(r.emoji) == ACCEPT_EMOJI, message.reactions)
        if reaction is None:
            return

        async for user in reaction.users():
            if user.id == self.bot.user.id:
                continue
            # Users who have since left the server come back as discord.User
            if not isinstance(user, discord.Member) or await self.grant_rules_role(user):
                await message.remove_reaction(ACCEPT_EMOJI, user)
    
    @send_welcome.before_loop
    async def before_send_welcome(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.send_welcome.cancel()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        Handle user reactions to messages

        - Listen for reaction to rules message, assign role

        Arguments:
            payload (RawReactionActionEvent): Payload containing
            attributes relating to the reaction event

        """
        # Match on the rules channel rather than the stored rules message so reactions
        # are still handled if send_welcome failed to run. The channel only ever
        # contains the rules message, as send_welcome deletes everything else.
        if payload.channel_id != self.bot.config["RULES_CHANNEL_ID"] or payload.member is None:
            return
        if payload.user_id == self.bot.user.id:
            return

        # Only remove the acceptance reaction once the role is granted, so a failed
        # attempt is retried by the sweep on next startup
        if str(payload.emoji) == ACCEPT_EMOJI and not await self.grant_rules_role(payload.member):
            return

        # Remove the acceptance reaction, and all other reactions to avoid confusion
        channel = self.bot.get_partial_messageable(payload.channel_id)
        message = channel.get_partial_message(payload.message_id)
        await message.remove_reaction(payload.emoji, payload.member)

    async def grant_rules_role(self, member: discord.Member) -> bool:
        """
        Give a member the rules accepted role

        Returns:
            bool: True if the member has the role
        """
        role_id = self.bot.config["RULES_ACCEPTED_ROLE"]
        role = member.guild.get_role(role_id)
        if role is None:
            log.error("Rules accepted role %s not found in guild %s", role_id, member.guild.id)
            return False
        if role in member.roles:
            return True

        try:
            await member.add_roles(role, reason="Accepted server rules")
        except discord.HTTPException:
            log.exception("Could not add rules accepted role to member %s", member.id)
            return False
        log.info("Added rules accepted role to member %s", member.id)
        return True

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(EdgeIXRules(bot))
