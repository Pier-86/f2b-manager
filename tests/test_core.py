import os
import pytest
from f2b_core import (
    Config, F2BError, format_duration, format_remaining,
    parse_duration, ascii_bar, sort_ips, ip_sort_key,
    SORT_MODES, t, get_presets, LogTailer, get_available_jails,
)


class TestFormatDuration:
    def test_permanent(self):
        assert format_duration(-1) == "permanente"

    def test_zero(self):
        assert format_duration(0) == "0s"

    def test_seconds_only(self):
        assert format_duration(45) == "45s"

    def test_minutes(self):
        assert format_duration(125) == "2m 5s"

    def test_hours(self):
        assert format_duration(3661) == "1h 1m 1s"

    def test_days(self):
        assert format_duration(90061) == "1g 1h 1m 1s"


class TestFormatRemaining:
    def test_permanent(self):
        assert format_remaining(-1) == "\u221e perm."

    def test_expired(self):
        assert format_remaining(0) == "scaduto"

    def test_negative(self):
        assert format_remaining(-5) == "scaduto"

    def test_days_no_hours(self):
        assert format_remaining(172800) == "2g"

    def test_days_with_hours(self):
        assert format_remaining(90000) == "1g 1h"

    def test_hours_with_minutes(self):
        assert format_remaining(3660) == "1h 1m"

    def test_minutes_only(self):
        assert format_remaining(120) == "2m"

    def test_seconds(self):
        assert format_remaining(30) == "30s"

    def test_none(self):
        assert format_remaining(None) == "\u2014"


class TestParseDuration:
    def test_seconds_int(self):
        assert parse_duration("3600") == 3600

    def test_permanent(self):
        assert parse_duration("-1") == -1

    def test_invalid_zero(self):
        assert parse_duration("0") is None

    def test_negative(self):
        assert parse_duration("-5") is None

    def test_days(self):
        assert parse_duration("2d") == 172800

    def test_hours_minutes(self):
        assert parse_duration("1h30m") == 5400

    def test_combined(self):
        assert parse_duration("1d2h30m15s") == 95415

    def test_whitespace(self):
        assert parse_duration("  5h  ") == 18000


class TestAsciiBar:
    def test_empty(self):
        assert ascii_bar(0, 0, 10) == "\u2591" * 10

    def test_full(self):
        assert ascii_bar(10, 10, 10) == "\u2588" * 10

    def test_half(self):
        assert ascii_bar(5, 10, 10) == "\u2588" * 5 + "\u2591" * 5

    def test_custom_width(self):
        res = ascii_bar(3, 10, 5)
        assert len(res) == 5
        assert res.count("\u2588") == 2


class TestIpSortKey:
    def test_valid_ip(self):
        key = ip_sort_key("192.168.1.1")
        assert str(key) == "192.168.1.1"

    def test_invalid_ip(self):
        key = ip_sort_key("not-an-ip")
        assert str(key) == "0.0.0.0"


class TestSortIps:
    def test_default(self):
        ips = ["2.2.2.2", "1.1.1.1"]
        assert sort_ips(ips, "default", {}) == ["2.2.2.2", "1.1.1.1"]

    def test_by_ip(self):
        ips = ["2.2.2.2", "1.1.1.1"]
        assert sort_ips(ips, "ip", {}) == ["1.1.1.1", "2.2.2.2"]

    def test_by_attempts(self):
        ips = ["1.1.1.1", "2.2.2.2"]
        stats = {"1.1.1.1": {"total_found": 10}, "2.2.2.2": {"total_found": 5}}
        assert sort_ips(ips, "attempts", stats) == ["1.1.1.1", "2.2.2.2"]

    def test_by_date(self):
        ips = ["1.1.1.1", "2.2.2.2"]
        stats = {"1.1.1.1": {"ban_time": "2024-01-01"}, "2.2.2.2": {"ban_time": "2024-06-01"}}
        assert sort_ips(ips, "date", stats) == ["2.2.2.2", "1.1.1.1"]


class TestSORT_MODES:
    def test_values(self):
        assert SORT_MODES == ["default", "ip", "date", "attempts"]


class TestI18n:
    def test_italian(self):
        assert t("dur_perm", "it") == "permanente"

    def test_english(self):
        assert t("dur_perm", "en") == "permanent"

    def test_fallback(self):
        assert t("nonexistent", "it") == "nonexistent"


class TestGetPresets:
    def test_default_labels(self):
        presets = get_presets()
        assert len(presets) == 7
        assert presets[0] == ("1 day", 86400)
        assert presets[-1] == ("Permanent", -1)

    def test_custom_labels(self):
        labels = ["A", "B"]
        presets = get_presets(labels)
        assert presets[0] == ("A", 86400)
        assert len(presets) == 2


class TestLogTailer:
    def test_no_such_file(self):
        tailer = LogTailer("/nonexistent/log.log")
        assert tailer.read_new_lines() == ""

    def test_parse_empty(self):
        tailer = LogTailer("/nonexistent/log.log")
        assert tailer.parse_events("sshd", {"1.1.1.1"}) == []


class TestConfig:
    def test_default_jail(self):
        assert Config().JAIL == "sshd"

    def test_default_db(self):
        assert Config().F2B_DB == "/var/lib/fail2ban/fail2ban.sqlite3"

    def test_set_active_jail(self):
        c = Config()
        c.ACTIVE_JAIL = "nginx-http-auth"
        assert c.JAIL == "nginx-http-auth"


class TestConfigEnv:
    def test_custom_jail(self, monkeypatch):
        monkeypatch.setenv("F2B_JAIL", "custom")
        assert Config().ACTIVE_JAIL == "custom"

    def test_custom_jails(self, monkeypatch):
        monkeypatch.setenv("F2B_JAILS", "jail1,jail2")
        c = Config()
        assert "jail1" in c.JAILS_ENV
        assert "jail2" in c.JAILS_ENV

    def test_custom_api_key(self, monkeypatch):
        monkeypatch.setenv("F2B_API_KEY", "secret123")
        assert Config().API_KEY == "secret123"

    def test_custom_db(self, monkeypatch):
        monkeypatch.setenv("F2B_DB", "/custom/db.sqlite3")
        assert Config().F2B_DB == "/custom/db.sqlite3"
