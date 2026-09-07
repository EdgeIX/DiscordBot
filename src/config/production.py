"""Runtime configuration loaded from environment variables."""

import os
from pathlib import Path


def _env(name: str, *aliases: str) -> str | None:
    for key in (name, *aliases):
        value = os.getenv(key)
        if value is not None and value.strip():
            return value.strip()
    return None


def _required(name: str, *aliases: str) -> str:
    value = _env(name, *aliases)
    if value is None:
        raise ValueError(f"Missing required configuration: {name}")
    return value


def _required_int(name: str, *aliases: str) -> int:
    value = _required(name, *aliases)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Configuration {name} must be an integer") from exc


def _boolean(name: str, default: bool) -> bool:
    value = _env(name)
    if value is None:
        return default
    return value.lower() not in {"0", "false", "no", "off"}


def _verify_ssl() -> bool:
    value = _env("IXPM_VERIFY_SSL")
    return value is None or value.lower() != "false"


def build_config(*, development: bool = False) -> dict:
    """Build validated runtime configuration for the selected environment."""

    source_dir = Path(__file__).resolve().parents[1]
    route_servers = {
        location: {
            name: {"url": _env(f"{location}_{name.upper()}")}
            for name in names
        }
        for location, names in {
            "SYD": ("rs1", "rs2"),
            "MEL": ("rs1", "rs2"),
            "ADL": ("rs1", "rs2"),
            "BNE": ("rs1", "rs2"),
            "PER": ("rs1", "rs2"),
            "DRW": ("rs1",),
            "HBA": ("rs1",),
        }.items()
    }

    return {
        "RULES_CHANNEL_ID": _required_int("RULES_CHANNEL_ID"),
        "RULES_ACCEPTED_ROLE": _required_int("RULES_ACCEPTED_ROLE"),
        "WELCOME_CHANNEL_ID": _required_int("WELCOME_CHANNEL_ID"),
        "ROLE_APPROVAL_CHANNEL_ID": _required_int("ROLE_APPROVAL_CHANNEL_ID"),
        "ANNOUNCEMENT_CHANNEL_ID": _required_int("ANNOUNCEMENT_CHANNEL_ID"),
        "TOKEN": _required("TOKEN", "DISCORD_TOKEN"),
        "IXPM_API_KEY": _required("IXPM_API_KEY"),
        "IXPM_PEER_INFO": _required("IXPM_PEER_INFO"),
        "IXPM_VERIFY_SSL": _verify_ssl(),
        "PEER_ROLE": _required_int("PEER_ROLE"),
        "GUILD_ID": _required_int("GUILD_ID", "DISCORD_GUILD"),
        "SRC_DIR": str(source_dir),
        "EVENTS_DIR": str(source_dir / "events"),
        "TASKS_DIR": str(source_dir / "tasks"),
        "EXTENSIONS_DIR": str(source_dir / "extensions"),
        "ROUTE_SERVERS": route_servers,
        "ENABLE_HOT_RELOAD": development and _boolean("ENABLE_HOT_RELOAD", True),
    }
