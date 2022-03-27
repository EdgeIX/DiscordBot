#!/usr/bin/env python3
import asyncio
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get

from utils.functions import format_message
from utils.constants import ASN_REGEX
from utils.config import get_conf_item

from menus.asn_approval import ApprovalMenuView

class ASNRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel = bot.get_channel(bot.config["ROLE_APPROVAL_CHANNEL_ID"])

    @app_commands.command(name="addasn", description="Add an ASN role to yourself!")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    async def add_asn(self, interaction: discord.Interaction, asn: int) -> discord.Embed:
        """
        """
        member = interaction.user
        match = ASN_REGEX.match(str(asn))
        if not match:
            user_message = await format_message("ASN Approval", f"Hi <@{member.id}>, {asn} is not a valid ASN!")
            await interaction.response.send_message(embed=user_message, ephemeral=True)
            return

        role = get(interaction.guild.roles, name=f"AS{asn}")
        asname = await self.bot.bgptoolkit.get_asn_name(asn)

        # Check if the user already has a role
        if role in member.roles:
            user_message = await format_message("ASN Approval", f"Hi <@{member.id}>, you already have a role for AS{asn}")
            await interaction.response.send_message(embed=user_message, ephemeral=True)
        else:
            user_message = await format_message("ASN Approval", f"Hi <@{member.id}>, your request to add yourself to AS{asn} ({asname}) has been queued for approval")
            staff_message = await format_message("ASN Approval", f"<@{member.id}> wishes to add themselves to AS{asn} ({asname}), please action this approval.")

            message_id = await interaction.response.send_message(embed=user_message)
            await self.channel.send(view=ApprovalMenuView(member, asn, interaction, asname),embed=staff_message)
    
    @app_commands.command(name="removeasn", description="Remove an ASN role from yourself")
    @app_commands.guilds(discord.Object(id=get_conf_item("GUILD_ID")))
    async def remove_asn(self, interaction: discord.Interaction, asn: int) -> discord.Embed:
        """
        Remove an ASN from a Member

        Arguments:
            asn (int): AS Number to remove
        """
        async def _other_roles(roles: discord.Member.roles, removed: discord.Role):
            """
            Iterate a Members roles to confirm if they have multiple ASNs

            Arguments:
                roles (discord.Member.roles): Member roles
                removed (discord.Role): Role that is currently being removed
            """
            for role in roles:
                if role.name.startswith("AS") and role.name != removed.name:
                    return True
            return False

        member = interaction.user
        match = ASN_REGEX.match(str(asn))
        if not match:
            user_message = await format_message("ASN Removal", f"Hi <@{member.id}>, {asn} is not a valid ASN!")
            await interaction.response.send_message(embed=user_message, ephemeral=True)
            return

        role = get(member.roles, name=f"AS{asn}")

        # Check if user has the role and remove it
        if role in member.roles:
            await member.remove_roles(get(interaction.guild.roles, name=role.name))

            # if the user has no other ASNs, remove the peer role
            if not await _other_roles(member.roles, role):
                peer_role = interaction.guild.get_role(self.bot.config["PEER_ROLE"])
                await member.remove_roles(get(interaction.guild.roles, name=peer_role.name))

            user_message = await format_message("ASN Removal", f"Hi <@{member.id}>, you have removed yourself from AS{asn}")
            await interaction.response.send_message(embed=user_message, ephemeral=True)
        else:
            user_message = await format_message("ASN Removal", f"Hi <@{member.id}>, you do not have a role for AS{asn}")
            await interaction.response.send_message(embed=user_message, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """Adds the cog to the bot"""
    await bot.add_cog(ASNRoles(bot))
