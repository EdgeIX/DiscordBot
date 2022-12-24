#!/usr/bin/env python3
import asyncio
import discord

from discord.utils import get

from utils.functions import format_message


class ApprovalMenu(discord.ui.Select):
    def __init__(self, requested: discord.User, original_interaction: discord.Interaction, asn: int, asname: str):
        """
        Approval Menu for ASN additions

        Arguments:
            requested (discord.User): Object of the user attempting to add a role
            asn (int): ASN number
            original_interaction (discord.Interaction): Original interaction of the request
            so we can update the original message.
            asname (str): Human readable AS Name
        """
        options = [
            discord.SelectOption(label="Approve",emoji="✅",description="Approve this users ASN addition"),
            discord.SelectOption(label="Deny",emoji="❌",description="Reject this users ASN addition"),
        ]
        self.requested = requested
        self.asn = asn
        self.og = original_interaction
        self.asname = asname
        super().__init__(placeholder="Approval Status", max_values=1, min_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        member = interaction.user.name

        if self.values[0] == "Approve":
            message = await format_message("ASN Approval", f"<@{self.requested.id}> has been granted role: AS{self.asn} ({self.asname}). Addition was approved by {member}")
            await interaction.response.edit_message(embed=message, view=None)
            original = await self.og.original_response()
            await original.edit(embed=message)
            await self.add_asn(interaction)
        elif self.values[0] == "Deny":
            message = await format_message("ASN Approval", f"<@{self.requested.id}> has not been granted role: AS{self.asn} ({self.asname}). Addition was rejected by {member}")
            await interaction.response.edit_message(embed=message, view=None)
            original = await self.og.original_response()
            await original.edit(embed=message)

    async def add_asn(self, interaction: discord.Interaction):
        """
        Add ASN Role

        Arguments:
            interaction (discord.Interaction): Instance of the current discord interaction to access
            roles and config.
        """
        if get(interaction.guild.roles, name=f"AS{self.asn}"):
            await self.requested.add_roles(get(interaction.guild.roles, name=f"AS{self.asn}"))
        else:
            role = await interaction.guild.create_role(name=f"AS{self.asn}")
            await self.requested.add_roles(role)
        
        # Perform check here via IXP to see if the ASN is a current peer of EdgeIX
        if self.asn in interaction.client.ixp.asns.keys():
            role = interaction.guild.get_role(interaction.client.config["PEER_ROLE"])
            await self.requested.add_roles(get(interaction.guild.roles, name=role.name))

        # Remove visitor role if present
        role = interaction.guild.get_role(interaction.client.config["RULES_ACCEPTED_ROLE"])
        await self.requested.remove_roles(get(interaction.guild.roles, name=role.name))

class ApprovalMenuView(discord.ui.View):
    def __init__(self, requested: discord.User, interaction: discord.Interaction, asn: int, asname: str, timeout = 7200):
        super().__init__(timeout=timeout)
        self.add_item(ApprovalMenu(requested, asn, interaction, asname))
