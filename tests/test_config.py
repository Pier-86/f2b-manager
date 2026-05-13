import os
from f2b_core import Config


class TestConfigDefaults:
    def test_default_jail(self):
        assert Config().JAIL == "sshd"

    def test_default_db(self):
        assert Config().F2B_DB == "/var/lib/fail2ban/fail2ban.sqlite3"

    def test_default_log(self):
        assert Config().F2B_LOG == "/var/log/fail2ban.log"

    def test_default_geoip_bin(self):
        assert Config().GEOIP_BIN == "geoiplookup"

    def test_default_api_rate(self):
        assert Config().API_RATE_LIMIT == 60

    def test_default_rate_window(self):
        assert Config().API_RATE_WINDOW == 60


class TestConfigEnv:
    def test_custom_jail(self, monkeypatch):
        monkeypatch.setenv("F2B_JAIL", "custom")
        assert Config().JAIL == "custom"

    def test_custom_api_key(self, monkeypatch):
        monkeypatch.setenv("F2B_API_KEY", "secret123")
        assert Config().API_KEY == "secret123"

    def test_custom_rate_limit(self, monkeypatch):
        monkeypatch.setenv("F2B_API_RATE_LIMIT", "100")
        assert Config().API_RATE_LIMIT == 100
