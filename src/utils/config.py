#!/usr/bin/env python3
"""Environment-aware, validated project configuration."""

import os

from config.production import build_config


def _is_development(value: str) -> bool:
    return value.strip().lower() in {"dev", "development", "local", "false", "0"}


class ProjectConfig:
    def __init__(self, environment: str | None = None) -> None:
        selected = environment or os.getenv("PYTHON_ENV", "dev")
        self.env = selected
        self.env_config = build_config(development=_is_development(selected))

    @property
    def c(self) -> dict:
        return self.env_config


def get_conf_item(key: str):
    """Return one validated setting for the current environment."""

    return ProjectConfig().c.get(key)
