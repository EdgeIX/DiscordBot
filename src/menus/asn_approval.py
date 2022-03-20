#!/usr/bin/env python3
import asyncio
import discord

from discord.utils import get

from utils.functions import format_message


class ApprovalMenu(discord.ui.Select):
    def __init__(self, requested: discord.User, asn: int, original_interaction: discord.Interaction):
        options = [
            discord.SelectOption(label="Approve",emoji="✅",description="Approve this users ASN addition"),
            discord.SelectOption(label="Deny",emoji="❌",description="Reject this users ASN addition"),
        ]
        self.requested = requested
        self.asn = asn
        self.og = original_interaction
        super().__init__(placeholder="Approval Status",max_values=1,min_values=1,options=options)
    
    async def callback(self, interaction: discord.Interaction):
        member = interaction.user.name
        if self.values[0] == "Approve":
            message = await format_message("ASN Approval", f"{self.requested} has been granted role: AS{self.asn}. Addition was approved by {member}")
            await interaction.response.edit_message(embed=message, view=None)
            test = await self.og.original_message()
            await test.edit(embed=message)
            await self.add_asn()
        elif self.values[0] == "Deny":
            message = await format_message("ASN Approval", f"{self.requested} has not been granted role: AS{self.asn}. Addition was rejected by {member}")
            await interaction.response.edit_message(embed=message, view=None)

    async def add_asn(self):
        """

        """
        if await get(discord.Guild.roles, name=self.asn):
            await self.requested.add_roles(discord.utils.get(discord.Guild.roles, name=self.asn))
            print("role added")
        else:
            print("no role!!")

class ApprovalMenuView(discord.ui.View):
    def __init__(self, requested: discord.User, asn: int, interaction: discord.Interaction, timeout = 7200):
        super().__init__(timeout=timeout)
        self.add_item(ApprovalMenu(requested, asn, interaction))
