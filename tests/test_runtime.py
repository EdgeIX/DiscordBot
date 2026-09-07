import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import discord

from utils.bot import EdgeIXBot
from utils.ixp import IXPManager
from tasks.route_servers import RouteServerLoop


@pytest.fixture
def configured_environment(monkeypatch):
    values = {
        "RULES_CHANNEL_ID": "1",
        "RULES_ACCEPTED_ROLE": "2",
        "WELCOME_CHANNEL_ID": "3",
        "ROLE_APPROVAL_CHANNEL_ID": "4",
        "ANNOUNCEMENT_CHANNEL_ID": "5",
        "TOKEN": "development-token",
        "IXPM_API_KEY": "development-key",
        "IXPM_PEER_INFO": "https://example.test/peers",
        "PEER_ROLE": "6",
        "GUILD_ID": "7",
        "PYTHON_ENV": "production",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)


@pytest.mark.asyncio
async def test_setup_hook_reuses_session_and_close_closes_it(configured_environment):
    bot = EdgeIXBot()
    bot.tree.sync = AsyncMock(return_value=[])

    async with bot:
        await bot._async_setup_hook()
        await bot.setup_hook()
        session = bot.session
        await bot.setup_hook()
        await asyncio.sleep(0)

        assert bot.session is session
        assert bot.tree.sync.await_count == 1
        assert not bot.failed_extensions
        assert len(bot.extensions) == 15
        commands = list(bot.tree.get_commands(guild=discord.Object(id=7)))
        assert len(commands) == 10
        assert {command.name for command in commands} == {
            "announcement", "addasn", "removeasn", "metrics", "peer",
            "peer-sessions", "gshut", "admin-sync", "whois", "whois-peering",
        }
        loop_tasks = [
            loop.get_task()
            for cog in bot.cogs.values()
            for name in ("get_route_server_data", "get_valid_peers", "send_welcome")
            for loop in [getattr(cog, name, None)]
            if hasattr(loop, "get_task")
        ]

    assert session.closed
    assert all(task is None or task.done() for task in loop_tasks)


def test_ixp_readers_tolerate_empty_or_malformed_cache():
    ixp = IXPManager()
    ixp.data = {"member_list": [{"asnum": "64500", "name": "Example"}], "ixp_list": []}
    ixp.make_ixp_dict()

    assert ixp.get_asn_data(64500)["name"] == "Example"
    assert ixp.get_asn_data("not-an-asn") is None


class _JSONResponse:
    def __init__(self, payload):
        self.status = 200
        self.payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False

    async def json(self):
        return self.payload


class _ResponseSession:
    def __init__(self, responses):
        self.responses = list(responses)

    def get(self, **_):
        return _JSONResponse(self.responses.pop(0))


@pytest.mark.asyncio
async def test_route_refresh_retains_cache_on_bad_schema_and_recovers():
    cached = {"protocols": {"old": {"state": "up"}}}
    route_data = {"SYD": {"rs1": {"url": "https://example.test/{protocol}", "data": {
        "ipv4": cached,
        "ipv6": cached,
    }}}}
    bot = SimpleNamespace(
        config={"ROUTE_SERVERS": route_data},
        session=_ResponseSession([
            {"protocols": {"broken": None}},
            {"protocols": {"broken": None}},
        ]),
        rs=SimpleNamespace(data={}),
    )
    cog = RouteServerLoop.__new__(RouteServerLoop)
    cog.bot = bot
    cog.route_server_data = route_data
    cog.console = SimpleNamespace(print=lambda *_: None)

    await cog.get_route_server_data()
    assert route_data["SYD"]["rs1"]["data"]["ipv4"] == cached
    assert route_data["SYD"]["rs1"]["error"] is True

    bot.session = _ResponseSession([
        {"protocols": {"new": {"state": "up"}}},
        {"protocols": {"new": {"state": "up"}}},
    ])
    await cog.get_route_server_data()
    assert "error" not in route_data["SYD"]["rs1"]
    assert route_data["SYD"]["rs1"]["data"]["ipv4"]["protocols"]["new"]["state"] == "up"


@pytest.mark.asyncio
async def test_ixpm_refresh_atomically_rejects_bad_id_and_recovers():
    ixp = IXPManager()
    ixp.data = {
        "member_list": [{"asnum": "64500", "name": "Old"}],
        "ixp_list": [{"ixp_id": 1, "shortname": "Old IXP"}],
    }
    ixp.asns = {64500: "Old"}
    ixp.ixp_id = {1: {"name": "Old IXP"}}
    bot = SimpleNamespace(
        config={
            "IXPM_API_KEY": "key",
            "IXPM_PEER_INFO": "https://example.test/peers",
            "IXPM_VERIFY_SSL": True,
        },
        session=_ResponseSession([
            {"member_list": [{"asnum": "64501", "name": "New"}], "ixp_list": [{"ixp_id": [], "shortname": "Bad"}]},
        ]),
        ixp=ixp,
    )
    from tasks.valid_peers import ValidPeerLoop

    cog = ValidPeerLoop.__new__(ValidPeerLoop)
    cog.bot = bot
    cog.console = SimpleNamespace(print=lambda *_: None)
    cog.headers = {"X-IXP-Manager-API-Key": "key"}

    await cog.get_valid_peers()
    assert ixp.data["member_list"][0]["name"] == "Old"
    assert ixp.asns == {64500: "Old"}
    assert ixp.ixp_id == {1: {"name": "Old IXP"}}

    bot.session = _ResponseSession([
        {"member_list": [{"asnum": "64501", "name": "New"}], "ixp_list": [{"ixp_id": 2, "shortname": "New IXP"}]},
    ])
    await cog.get_valid_peers()
    assert ixp.asns == {64501: "New"}
    assert ixp.ixp_id == {2: {"name": "New IXP"}}
