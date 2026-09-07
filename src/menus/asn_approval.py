#!/usr/bin/env python3
import asyncio
import discord

from utils.functions import format_message
from utils.decorators import user_has_permissions
from utils.permissions import GLOBAL_ADMIN_PERMISSION


class RoleConfigurationError(RuntimeError):
    """Configured Discord role is unavailable in the approval guild."""


class ApprovalMenu(discord.ui.Select):
    def __init__(
        self,
        requested: discord.Member,
        asn: int,
        asname: str,
        request_channel_id: int = None,
        request_message_id: int = None,
    ):
        """
        Approval Menu for ASN additions

        Arguments:
            requested (discord.User): Object of the user attempting to add a role
            asn (int): ASN number
            asname (str): Human readable AS Name
        """
        options = [
            discord.SelectOption(label="Approve",emoji="✅",description="Approve this users ASN addition"),
            discord.SelectOption(label="Deny",emoji="❌",description="Reject this users ASN addition"),
        ]
        self.requested = requested
        self.asn = asn
        self.asname = asname
        self.request_channel_id = request_channel_id
        self.request_message_id = request_message_id
        self._action_lock = asyncio.Lock()
        self._resolved = False
        super().__init__(placeholder="Approval Status", max_values=1, min_values=1, options=options)

    async def _send_ephemeral(self, interaction: discord.Interaction, embed: discord.Embed):
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _notify_requester(self, interaction: discord.Interaction, embed: discord.Embed):
        """Best-effort update through the bot-authenticated channel API."""
        if self.request_channel_id is None or self.request_message_id is None:
            return
        try:
            channel = interaction.client.get_channel(self.request_channel_id)
            if channel is None:
                channel = await interaction.client.fetch_channel(self.request_channel_id)
            message = await channel.fetch_message(self.request_message_id)
            await message.edit(embed=embed)
        except (AttributeError, discord.Forbidden, discord.HTTPException, discord.NotFound):
            return

    async def callback(self, interaction: discord.Interaction):
        decision = self.values[0]
        if not user_has_permissions(interaction.user, GLOBAL_ADMIN_PERMISSION):
            message = await format_message("ASN Approval", "You are not authorised to action ASN approvals.")
            await self._send_ephemeral(interaction, message)
            return

        await interaction.response.defer()
        async with self._action_lock:
            if self._resolved:
                message = await format_message("ASN Approval", "This ASN approval has already been actioned.")
                await self._send_ephemeral(interaction, message)
                return

            member = interaction.user.name
            if decision == "Approve":
                try:
                    await self.add_asn(interaction)
                except RoleConfigurationError:
                    message = await format_message(
                        "ASN Approval",
                        "ASN approval could not be completed because a configured Discord role is missing. Contact staff.",
                    )
                    await self._send_ephemeral(interaction, message)
                    return
                except (discord.Forbidden, discord.HTTPException):
                    message = await format_message(
                        "ASN Approval",
                        "ASN role update failed and changes may be partial. Approval was not recorded; contact staff before retrying.",
                    )
                    await self._send_ephemeral(interaction, message)
                    return
                message = await format_message(
                    "ASN Approval",
                    f"<@{self.requested.id}> has been granted role: AS{self.asn} ({self.asname}). Addition was approved by {member}",
                )
            elif decision == "Deny":
                message = await format_message(
                    "ASN Approval",
                    f"<@{self.requested.id}> has not been granted role: AS{self.asn} ({self.asname}). Addition was rejected by {member}",
                )
            else:
                message = await format_message("ASN Approval", "Unknown approval action.")
                await self._send_ephemeral(interaction, message)
                return

            self._resolved = True
            await interaction.edit_original_response(embed=message, view=None)
            await self._notify_requester(interaction, message)

    async def add_asn(self, interaction: discord.Interaction):
        """
        Add ASN Role

        Arguments:
            interaction (discord.Interaction): Instance of the current discord interaction to access
            roles and config.
        """
        peer_role = interaction.guild.get_role(interaction.client.config["PEER_ROLE"])
        rules_role = interaction.guild.get_role(interaction.client.config["RULES_ACCEPTED_ROLE"])
        if peer_role is None or rules_role is None:
            raise RoleConfigurationError

        role = discord.utils.get(interaction.guild.roles, name=f"AS{self.asn}")
        if role:
            await self.requested.add_roles(role)
        else:
            role = await interaction.guild.create_role(name=f"AS{self.asn}")
            await self.requested.add_roles(role)
        
        # Perform check here via IXP to see if the ASN is a current peer of EdgeIX
        if self.asn in interaction.client.ixp.asns.keys():
            await self.requested.add_roles(peer_role)

        # Remove visitor role if present
        await self.requested.remove_roles(rules_role)

class ApprovalMenuView(discord.ui.View):
    def __init__(
        self,
        requested: discord.Member,
        asn: int,
        asname: str,
        request_channel_id: int = None,
        request_message_id: int = None,
        timeout=7200,
    ):
        super().__init__(timeout=timeout)
        self.add_item(
            ApprovalMenu(
                requested=requested,
                asn=asn,
                asname=asname,
                request_channel_id=request_channel_id,
                request_message_id=request_message_id,
            )
        )
