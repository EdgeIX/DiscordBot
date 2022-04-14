#!/usr/bin/env python3
import asyncio
from typing import Optional

import discord
from discord.ext import commands, tasks

from utils.functions import format_message

class EdgeIXRules(commands.Cog):
    """
        Post rules to a channel to allow users to interact to gain
        further role privileges
    """
    def __init__(self, bot):
        self.bot = bot
        self.channel = bot.get_channel(bot.config["RULES_CHANNEL_ID"])

        self.send_welcome.start()
    
    @tasks.loop(count=1)
    async def send_welcome(self):
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

        await self.bot.rules_msg.add_reaction("\U00002705")
    
    @send_welcome.before_loop
    async def before_send_welcome(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        Handle user reactions to messages

        - Listen for reaction to rules message, assign role

        Arguments:
            payload (RawReactionActionEvent): Payload containing
            attributes relating to the reaction event

        """
        # Check if this message is the message in bot.rules_msg.id. payload.emoji doesnt return a valid
        # id, meaning we have to use the literal emoji in this code :(
        if payload.message_id == self.bot.rules_msg.id and payload.emoji.name == "✅":
            # Don't execute when the bot adds the initial reaction
            if payload.user_id == self.bot.user.id:
                return
            
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(self.bot.config["RULES_ACCEPTED_ROLE"])

            await payload.member.add_roles(discord.utils.get(guild.roles, name=role.name))
            await self.bot.rules_msg.remove_reaction(payload.emoji.name, payload.member)

        # Remove all other reactions to avoid confusion
        elif payload.message_id == self.bot.rules_msg.id:
            await self.bot.rules_msg.remove_reaction(payload.emoji.name, payload.member)

async def setup(bot):
    """Adds the cog to the bot"""
    await bot.add_cog(EdgeIXRules(bot))
