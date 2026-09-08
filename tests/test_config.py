import pytest

from utils.config import ProjectConfig


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
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("ENABLE_HOT_RELOAD", raising=False)
    return values


def test_project_config_validates_and_uses_portable_paths(configured_environment):
    config = ProjectConfig("dev").c

    assert config["GUILD_ID"] == 7
    assert config["ENABLE_HOT_RELOAD"] is True
    assert config["EVENTS_DIR"].endswith("src/events")


def test_hot_reload_is_forced_off_outside_development(configured_environment, monkeypatch):
    monkeypatch.setenv("ENABLE_HOT_RELOAD", "true")

    assert ProjectConfig("production").c["ENABLE_HOT_RELOAD"] is False


def test_ixpm_ssl_only_false_disables_verification(configured_environment, monkeypatch):
    monkeypatch.setenv("IXPM_VERIFY_SSL", " NO ")
    assert ProjectConfig("production").c["IXPM_VERIFY_SSL"] is True

    monkeypatch.setenv("IXPM_VERIFY_SSL", " false ")
    assert ProjectConfig("production").c["IXPM_VERIFY_SSL"] is False


def test_missing_setting_fails_with_setting_name(configured_environment, monkeypatch):
    monkeypatch.delenv("TOKEN")

    with pytest.raises(ValueError, match="TOKEN"):
        ProjectConfig("production")
