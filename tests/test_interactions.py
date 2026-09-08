import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import discord
import pytest

from menus.asn_approval import ApprovalMenu
from utils.permissions import GLOBAL_ADMIN_PERMISSION


class FakeRole:
    def __init__(self, role_id, name):
        self.id = role_id
        self.name = name


class FakeMember:
    id = 100
    name = "staff"

    def __init__(self, roles=()):
        self.roles = list(roles)
        self.added = []
        self.removed = []

    def get_role(self, role_id):
        return next((role for role in self.roles if role.id == role_id), None)

    async def add_roles(self, role):
        self.added.append(role)

    async def remove_roles(self, role):
        self.removed.append(role)


class FakeGuild:
    def __init__(self, roles=()):
        self.roles = list(roles)

    def get_role(self, role_id):
        return next((role for role in self.roles if role.id == role_id), None)

    async def create_role(self, name):
        role = FakeRole(1000 + len(self.roles), name)
        self.roles.append(role)
        return role


class FakeResponse:
    def __init__(self):
        self.done = False
        self.deferred = False
        self.messages = []

    def is_done(self):
        return self.done

    async def defer(self, **kwargs):
        self.done = True
        self.deferred = True

    async def send_message(self, **kwargs):
        self.done = True
        self.messages.append(kwargs)


class FakeFollowup:
    def __init__(self):
        self.messages = []

    async def send(self, **kwargs):
        self.messages.append(kwargs)


class FakeInteraction:
    def __init__(self, user, guild, client):
        self.user = user
        self.guild = guild
        self.client = client
        self.response = FakeResponse()
        self.followup = FakeFollowup()
        self.edits = []
        self.channel_id = None

    async def edit_original_response(self, **kwargs):
        self.edits.append(kwargs)


class ApprovalTestMenu(ApprovalMenu):
    def __init__(self, *args, decision="Approve", **kwargs):
        super().__init__(*args, **kwargs)
        self.decision = decision

    @property
    def values(self):
        return [self.decision]


def approval_client(asns=()):
    return SimpleNamespace(
        config={"PEER_ROLE": 10, "RULES_ACCEPTED_ROLE": 11},
        ixp=SimpleNamespace(asns={asn: True for asn in asns}),
    )


def approval_guild():
    return FakeGuild([FakeRole(10, "peer"), FakeRole(11, "visitor")])


def staff_member():
    return FakeMember([FakeRole(GLOBAL_ADMIN_PERMISSION[0], "staff")])


def make_approval(decision="Approve", *, requester=None, asns=()):
    requester = requester or FakeMember()
    menu = ApprovalTestMenu(requested=requester, asn=64500, asname="Example", decision=decision)
    guild = approval_guild()
    interaction = FakeInteraction(staff_member(), guild, approval_client(asns))
    return menu, requester, interaction


@pytest.mark.asyncio
async def test_approval_rejects_unauthorised_staff():
    menu, requester, interaction = make_approval()
    interaction.user = FakeMember([FakeRole(999, "member")])

    await menu.callback(interaction)

    assert interaction.response.messages
    assert interaction.response.messages[0]["ephemeral"] is True
    assert not requester.added
    assert not interaction.edits


@pytest.mark.asyncio
async def test_approval_defers_and_applies_roles_before_success():
    menu, requester, interaction = make_approval(asns=(64500,))

    await menu.callback(interaction)

    assert interaction.response.deferred
    assert requester.added[0].name == "AS64500"
    assert requester.added[1].name == "peer"
    assert requester.removed[0].name == "visitor"
    assert interaction.edits
    assert menu._resolved


@pytest.mark.asyncio
async def test_approval_does_not_use_expired_original_interaction():
    menu, requester, interaction = make_approval()
    interaction.original_response = None

    await menu.callback(interaction)

    assert interaction.edits
    assert requester.added


@pytest.mark.asyncio
async def test_approval_serializes_duplicate_clicks():
    menu, requester, interaction = make_approval()
    calls = 0

    async def slow_add_asn(_interaction):
        nonlocal calls
        calls += 1
        await asyncio.sleep(0)

    menu.add_asn = slow_add_asn
    duplicate = FakeInteraction(staff_member(), interaction.guild, interaction.client)

    await asyncio.gather(menu.callback(interaction), menu.callback(duplicate))

    assert calls == 1
    assert len(interaction.edits) == 1
    assert duplicate.followup.messages
    assert "already" in duplicate.followup.messages[0]["embed"].fields[0].value


@pytest.mark.asyncio
async def test_approval_reports_missing_configured_roles():
    menu, requester, interaction = make_approval()
    interaction.guild.roles = []

    await menu.callback(interaction)

    assert not interaction.edits
    assert interaction.followup.messages
    assert "configured Discord role" in interaction.followup.messages[0]["embed"].fields[0].value
    assert not requester.added


@pytest.mark.asyncio
async def test_approval_reports_partial_role_failure():
    menu, requester, interaction = make_approval()
    failure = discord.HTTPException(SimpleNamespace(status=500, reason="failure", headers={}), "failed")
    menu.add_asn = AsyncMock(side_effect=failure)

    await menu.callback(interaction)

    assert not interaction.edits
    assert interaction.followup.messages
    assert "may be partial" in interaction.followup.messages[0]["embed"].fields[0].value
    assert not menu._resolved


@pytest.fixture
def configured_environment(monkeypatch):
    values = {
        "RULES_CHANNEL_ID": "1",
        "RULES_ACCEPTED_ROLE": "11",
        "WELCOME_CHANNEL_ID": "3",
        "ROLE_APPROVAL_CHANNEL_ID": "4",
        "ANNOUNCEMENT_CHANNEL_ID": "5",
        "TOKEN": "development-token",
        "IXPM_API_KEY": "development-key",
        "IXPM_PEER_INFO": "https://example.test/peers",
        "PEER_ROLE": "10",
        "GUILD_ID": "7",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)


def test_legacy_sync_requires_global_admin_role(configured_environment):
    from extensions.sync import CommandSync

    check = CommandSync.admin_sync_legacy.checks[0]
    allowed = SimpleNamespace(author=staff_member(), guild=approval_guild())
    denied = SimpleNamespace(author=FakeMember([FakeRole(999, "member")]), guild=approval_guild())

    assert check(allowed) is True
    with pytest.raises(Exception):
        check(denied)


@pytest.mark.asyncio
async def test_whois_peering_empty_and_long_results(configured_environment):
    from extensions.whoispeering import WhoIsPeering
    from utils.enums import PeeringLocations

    bot = SimpleNamespace(rs=SimpleNamespace(peers_by_location=lambda _: []))
    empty_interaction = FakeInteraction(staff_member(), approval_guild(), bot)
    cog = WhoIsPeering(bot)
    await cog.whois_peering.callback(cog, empty_interaction, PeeringLocations.Sydney)

    assert empty_interaction.response.deferred
    assert len(empty_interaction.followup.messages) == 1
    assert "No peers" in empty_interaction.followup.messages[0]["embed"].fields[0].value

    peers = [f"AS{index}" for index in range(500)]
    bot.rs.peers_by_location = lambda _: peers
    long_interaction = FakeInteraction(staff_member(), approval_guild(), bot)
    await cog.whois_peering.callback(cog, long_interaction, PeeringLocations.Sydney)

    values = [message["embed"].fields[0].value for message in long_interaction.followup.messages]
    assert len(values) > 1
    assert all(len(value) <= 1024 for value in values)
