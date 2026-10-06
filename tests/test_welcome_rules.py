from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from tasks.welcome_rules import ACCEPT_EMOJI, EdgeIXRules

RULES_CHANNEL_ID = 1
RULES_ROLE_ID = 11
BOT_USER_ID = 999


def make_member(member_id=100, roles=(), add_roles_error=None):
    role = SimpleNamespace(id=RULES_ROLE_ID)
    member = MagicMock(spec=discord.Member)
    member.id = member_id
    member.roles = list(roles)
    member.guild = SimpleNamespace(id=7, get_role=lambda role_id: role if role_id == RULES_ROLE_ID else None)
    member.add_roles = AsyncMock(side_effect=add_roles_error)
    return member, role


def make_cog():
    message = SimpleNamespace(remove_reaction=AsyncMock())
    channel = SimpleNamespace(get_partial_message=MagicMock(return_value=message))
    bot = SimpleNamespace(
        config={"RULES_CHANNEL_ID": RULES_CHANNEL_ID, "RULES_ACCEPTED_ROLE": RULES_ROLE_ID},
        user=SimpleNamespace(id=BOT_USER_ID),
        get_partial_messageable=MagicMock(return_value=channel),
    )
    cog = EdgeIXRules.__new__(EdgeIXRules)
    cog.bot = bot
    return cog, message


def make_payload(member, emoji=ACCEPT_EMOJI, channel_id=RULES_CHANNEL_ID):
    return SimpleNamespace(
        channel_id=channel_id,
        message_id=50,
        user_id=member.id,
        member=member,
        emoji=discord.PartialEmoji(name=emoji),
    )


async def test_accept_reaction_grants_role_without_stored_rules_message():
    cog, message = make_cog()
    member, role = make_member()

    await cog.on_raw_reaction_add(make_payload(member))

    member.add_roles.assert_awaited_once_with(role, reason="Accepted server rules")
    message.remove_reaction.assert_awaited_once()


async def test_failed_grant_keeps_reaction_for_startup_sweep():
    cog, message = make_cog()
    member, _ = make_member(add_roles_error=discord.Forbidden(MagicMock(status=403), "Missing Permissions"))

    await cog.on_raw_reaction_add(make_payload(member))

    message.remove_reaction.assert_not_awaited()


async def test_other_reactions_are_removed_without_granting_role():
    cog, message = make_cog()
    member, _ = make_member()

    await cog.on_raw_reaction_add(make_payload(member, emoji="\U0001F600"))

    member.add_roles.assert_not_awaited()
    message.remove_reaction.assert_awaited_once()


async def test_reactions_outside_rules_channel_are_ignored():
    cog, message = make_cog()
    member, _ = make_member()

    await cog.on_raw_reaction_add(make_payload(member, channel_id=2))

    member.add_roles.assert_not_awaited()
    message.remove_reaction.assert_not_awaited()


async def test_sweep_grants_pending_acceptances_and_clears_reactions():
    cog, _ = make_cog()
    pending, role = make_member(member_id=100)
    already_accepted, accepted_role = make_member(member_id=101)
    already_accepted.roles = [accepted_role]
    failing, _ = make_member(member_id=102, add_roles_error=discord.HTTPException(MagicMock(status=500), "error"))
    departed = SimpleNamespace(id=103)
    bot_user = SimpleNamespace(id=BOT_USER_ID)

    async def users():
        for user in (bot_user, pending, already_accepted, failing, departed):
            yield user

    reaction = SimpleNamespace(emoji=ACCEPT_EMOJI, users=users)
    message = SimpleNamespace(reactions=[reaction], remove_reaction=AsyncMock())

    await cog.sweep_pending_acceptances(message)

    pending.add_roles.assert_awaited_once_with(role, reason="Accepted server rules")
    already_accepted.add_roles.assert_not_awaited()
    removed = [call.args[1] for call in message.remove_reaction.await_args_list]
    assert removed == [pending, already_accepted, departed]


@pytest.mark.parametrize("reactions", [[], [SimpleNamespace(emoji="\U0001F600")]])
async def test_sweep_without_accept_reaction_does_nothing(reactions):
    cog, _ = make_cog()
    message = SimpleNamespace(reactions=reactions, remove_reaction=AsyncMock())

    await cog.sweep_pending_acceptances(message)

    message.remove_reaction.assert_not_awaited()
