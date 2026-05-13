#!/usr/bin/env python3
import os
import re
import time
import shlex
import logging
import sqlite3
import subprocess
import ipaddress
from pathlib import Path

logger = logging.getLogger(__name__)


DEFAULT_PATHS = {
    "f2b_db": "/var/lib/fail2ban/fail2ban.sqlite3",
    "f2b_log": "/var/log/fail2ban.log",
    "f2b_sock": "/var/run/fail2ban/fail2ban.sock",
    "f2b_client": "fail2ban-client",
}

SYNOLOGY_ALT_PATHS = [
    {
        "f2b_db": "/volume1/@appstore/fail2ban/var/lib/fail2ban/fail2ban.sqlite3",
        "f2b_log": "/volume1/@appstore/fail2ban/var/log/fail2ban.log",
        "f2b_sock": "/var/run/fail2ban/fail2ban.sock",
        "f2b_client": "/usr/local/fail2ban/bin/fail2ban-client",
    },
    {
        "f2b_db": "/opt/var/lib/fail2ban/fail2ban.sqlite3",
        "f2b_log": "/opt/var/log/fail2ban.log",
        "f2b_sock": "/opt/var/run/fail2ban/fail2ban.sock",
        "f2b_client": "/opt/bin/fail2ban-client",
    },
]


DEFAULT_JAILS_CONFIG = {
    "sshd": {
        "name": "SSH",
        "icon": "\U0001f512",
        "log": "/var/log/auth.log",
        "log_pattern": r"sshd\[",
    },
    "synology-dsm": {
        "name": "Synology DSM",
        "icon": "\U0001f4e1",
        "log": "/var/log/synolog/synolog.log",
        "log_pattern": r"synology-dsm",
    },
    "nginx-http-auth": {
        "name": "Nginx HTTP Auth",
        "icon": "\U0001f310",
        "log": "/var/log/nginx/error.log",
        "log_pattern": r"nginx",
    },
    "postfix": {
        "name": "Postfix SMTP",
        "icon": "\u2709\ufe0f",
        "log": "/var/log/mail.log",
        "log_pattern": r"postfix",
    },
    "roundcube": {
        "name": "Roundcube Webmail",
        "icon": "\U0001f4e8",
        "log": "/var/log/roundcubemail/errors.log",
        "log_pattern": r"roundcube",
    },
    "openvpn": {
        "name": "OpenVPN",
        "icon": "\U0001f310",
        "log": "/var/log/openvpn.log",
        "log_pattern": r"openvpn",
    },
}


def detect_platform_paths() -> dict:
    if os.path.exists("/etc/synoinfo.conf"):
        logger.info("Synology platform detected")
        for alt in SYNOLOGY_ALT_PATHS:
            if os.path.exists(alt["f2b_db"]) or os.path.exists(alt["f2b_sock"]):
                logger.info("Using Synology paths: %s", alt)
                return alt
    return DEFAULT_PATHS


def detect_jails() -> list[dict]:
    found = []
    try:
        out = run("fail2ban-client status", check=False)
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("- "):
                jail_name = line[2:].strip()
                if jail_name:
                    info = DEFAULT_JAILS_CONFIG.get(jail_name, {
                        "name": jail_name,
                        "icon": "\U0001f6e1\ufe0f",
                        "log": "/var/log/fail2ban.log",
                        "log_pattern": jail_name,
                    })
                    info["jail"] = jail_name
                    found.append(info)
    except Exception as e:
        logger.warning("Jail detection failed: %s", e)
    return found


class Config:
    def __init__(self):
        platform_paths = detect_platform_paths()
        self.JAILS_ENV = [j.strip() for j in os.environ.get("F2B_JAILS", "sshd").split(",") if j.strip()]
        self.ACTIVE_JAIL = os.environ.get("F2B_JAIL", self.JAILS_ENV[0] if self.JAILS_ENV else "sshd")
        self.F2B_DB = os.environ.get("F2B_DB", platform_paths["f2b_db"])
        self.F2B_LOG = os.environ.get("F2B_LOG", platform_paths["f2b_log"])
        self.F2B_SOCK = os.environ.get("F2B_SOCK", platform_paths["f2b_sock"])
        self.F2B_CLIENT = os.environ.get("F2B_CLIENT", platform_paths["f2b_client"])
        self.GEOIP_BIN = os.environ.get("F2B_GEOIP_BIN", "geoiplookup")
        self.API_KEY = os.environ.get("F2B_API_KEY", "")
        self.API_RATE_LIMIT = int(os.environ.get("F2B_API_RATE_LIMIT", "60"))
        self.API_RATE_WINDOW = int(os.environ.get("F2B_API_RATE_WINDOW", "60"))

    @property
    def JAIL(self):
        return self.ACTIVE_JAIL

    @JAIL.setter
    def JAIL(self, value):
        self.ACTIVE_JAIL = value


def get_client():
    cfg = Config()
    return cfg.F2B_CLIENT


class F2BError(Exception):
    pass


_JAIL_RE = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')


def _validate_ip(ip: str) -> str:
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        raise F2BError(f"Invalid IP address: {ip!r}")


def _validate_jail(jail: str) -> str:
    if not _JAIL_RE.match(jail):
        raise F2BError(f"Invalid jail name: {jail!r}")
    return jail


def run(cmd: str, check: bool = True) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise F2BError(f"Command failed (code {result.returncode}): {cmd[:80]}  stderr={result.stderr.strip()}")
    return result.stdout.strip()


# ── jail management ──────────────────────────────────────────────────

def get_available_jails() -> list[dict]:
    detected = detect_jails()
    cfg = Config()
    env_jails = cfg.JAILS_ENV
    if env_jails and env_jails != [""]:
        configured = []
        for j in env_jails:
            j = j.strip()
            existing = next((d for d in detected if d["jail"] == j), None)
            if existing:
                configured.append(existing)
            else:
                info = DEFAULT_JAILS_CONFIG.get(j, {
                    "name": j, "icon": "\U0001f6e1\ufe0f",
                    "log": cfg.F2B_LOG, "log_pattern": j,
                })
                info["jail"] = j
                configured.append(info)
        return configured
    return detected


def get_jail_status(jail: str = None, config: Config = None) -> dict:
    if config is None:
        config = Config()
    j = _validate_jail(jail or config.JAIL)
    client = config.F2B_CLIENT
    out = run(f"{client} status {j}")
    banned_ips, total_failed, total_banned = [], 0, 0
    for line in out.splitlines():
        if "Currently banned" in line:
            try:
                total_banned = int(line.split(":")[-1].strip())
            except ValueError:
                pass
        if "Total failed" in line:
            try:
                total_failed = int(line.split(":")[-1].strip())
            except ValueError:
                pass
        if "Banned IP list" in line:
            ips_str = line.split(":")[-1].strip()
            if ips_str:
                banned_ips = ips_str.split()
    return {"banned_ips": banned_ips, "total_failed": total_failed, "total_banned": total_banned, "jail": j}


def get_jail_bantime(jail: str = None, config: Config = None) -> int:
    if config is None:
        config = Config()
    j = _validate_jail(jail or config.JAIL)
    client = config.F2B_CLIENT
    try:
        out = run(f"{client} get {j} bantime")
        return int(out) if out.lstrip("-").isdigit() else 0
    except (F2BError, ValueError):
        return 0


def set_jail_bantime(seconds: int, jail: str = None, config: Config = None):
    if config is None:
        config = Config()
    j = _validate_jail(jail or config.JAIL)
    client = config.F2B_CLIENT
    run(f"{client} set {j} bantime {seconds}")


def unban_ip(ip: str, jail: str = None, config: Config = None) -> bool:
    if config is None:
        config = Config()
    j = _validate_jail(jail or config.JAIL)
    _validate_ip(ip)
    client = config.F2B_CLIENT
    result = run(f"{client} set {j} unbanip {ip}")
    return "1" in result or result == ip


def reban_ip(ip: str, seconds: int, jail: str = None, config: Config = None) -> bool:
    if config is None:
        config = Config()
    j = _validate_jail(jail or config.JAIL)
    _validate_ip(ip)
    client = config.F2B_CLIENT
    original = get_jail_bantime(j, config)
    r_unban = run(f"{client} set {j} unbanip {ip}")
    if "1" not in r_unban:
        return False
    run(f"{client} set {j} bantime {seconds}")
    r_ban = run(f"{client} set {j} banip {ip}")
    run(f"{client} set {j} bantime {original}")
    return "1" in r_ban


# ── SQLite queries ─────────────────────────────────────────────────────

def get_remaining_bantimes(ips: list, jail: str = None, config: Config = None) -> dict:
    if config is None:
        config = Config()
    j = _validate_jail(jail or config.JAIL)
    if not ips:
        return {}
    ips_set = set(ips)
    now = time.time()
    result = {}
    try:
        conn = sqlite3.connect(config.F2B_DB)
        try:
            rows = conn.execute(
                "SELECT ip, timeofban, bantime FROM bans WHERE jail=?", (j,)
            ).fetchall()
        finally:
            conn.close()
        for ip, timeofban, bantime in rows:
            if ip not in ips_set:
                continue
            bantime = int(bantime)
            if bantime == -1:
                result[ip] = -1
            else:
                result[ip] = max(0, int((timeofban + bantime) - now))
    except Exception as e:
        logger.warning("SQLite remaining bantimes (%s): %s", j, e)
    return result


def get_historical_count(jail: str = None, config: Config = None) -> int:
    if config is None:
        config = Config()
    j = _validate_jail(jail or config.JAIL)
    try:
        conn = sqlite3.connect(config.F2B_DB)
        try:
            row = conn.execute(
                "SELECT COUNT(DISTINCT ip) FROM bans WHERE jail=?", (j,)
            ).fetchone()
        finally:
            conn.close()
        return row[0] if row else 0
    except Exception as e:
        logger.warning("SQLite historical count (%s): %s", j, e)
        return 0


# ── incremental log parser ────────────────────────────────────────────

def _make_jail_regex(jail: str):
    escaped = re.escape(jail)
    return {
        "ban": re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[' + escaped + r'\] Ban (\S+)$'),
        "found": re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[' + escaped + r'\] Found (\S+)'),
        "unban": re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[' + escaped + r'\] Unban (\S+)$'),
    }


class LogTailer:
    def __init__(self, path: str = "/var/log/fail2ban.log"):
        self.path = path
        self._pos = 0
        self._ino = 0

    def _stat(self):
        try:
            st = os.stat(self.path)
            return st.st_ino, st.st_size
        except OSError:
            return 0, 0

    def read_new_lines(self) -> str:
        ino, size = self._stat()
        if not ino:
            self._pos = 0
            self._ino = 0
            return ""
        if ino != self._ino:
            self._ino = ino
            self._pos = 0
        if size < self._pos:
            self._pos = 0
        if size == self._pos:
            return ""
        try:
            with open(self.path, "r", errors="replace") as f:
                f.seek(self._pos)
                data = f.read()
                self._pos = f.tell()
                self._ino = ino
                return data
        except OSError:
            return ""

    def parse_events(self, jail: str = "sshd", ips: set = None) -> list:
        data = self.read_new_lines()
        if not data:
            return []
        regexes = _make_jail_regex(jail)
        events = []
        for line in data.splitlines():
            m = regexes["ban"].match(line)
            if m:
                ip = m.group(2)
                if ips is None or ip in ips:
                    events.append({"type": "ban", "ip": ip, "ts": m.group(1), "raw": line})
                continue
            m = regexes["unban"].match(line)
            if m:
                ip = m.group(2)
                if ips is None or ip in ips:
                    events.append({"type": "unban", "ip": ip, "ts": m.group(1), "raw": line})
                continue
            m = regexes["found"].match(line)
            if m:
                ip = m.group(2)
                if ips is None or ip in ips:
                    events.append({"type": "found", "ip": ip, "ts": m.group(1), "raw": line})
        return events


_LOG_TAILERS: dict[str, LogTailer] = {}


def _get_tailer(config: Config = None):
    if config is None:
        config = Config()
    path = config.F2B_LOG
    if path not in _LOG_TAILERS:
        _LOG_TAILERS[path] = LogTailer(path)
    return _LOG_TAILERS[path]


def get_ip_stats(ips: list, jail: str = None, config: Config = None) -> dict:
    if config is None:
        config = Config()
    j = jail or config.JAIL
    if not ips:
        return {}
    ips_set = set(ips)
    tailer = _get_tailer(config)
    events = tailer.parse_events(j, ips_set)

    result = {ip: {"ban_time": None, "total_found": 0, "found_after_ban": 0} for ip in ips}
    for ev in events:
        ip = ev["ip"]
        if ip not in result:
            continue
        if ev["type"] == "ban":
            result[ip]["ban_time"] = ev["ts"]
        elif ev["type"] == "found":
            result[ip]["total_found"] += 1
    for ip in result:
        bt = result[ip]["ban_time"]
        if bt:
            result[ip]["found_after_ban"] = sum(
                1 for ev in events if ev["ip"] == ip and ev["type"] == "found" and ev["ts"] > bt
            )
        result[ip]["ban_time"] = result[ip]["ban_time"] or "—"
    return result


def get_top_ips(n: int = 5, jail: str = None, config: Config = None) -> list:
    if config is None:
        config = Config()
    j = _validate_jail(jail or config.JAIL)
    escaped = re.escape(j)
    out = run(f"grep '\\[{escaped}\\] Found' {shlex.quote(config.F2B_LOG)} 2>/dev/null || true")
    regex = _make_jail_regex(j)["found"]
    counts = {}
    for line in out.splitlines():
        m = regex.match(line)
        if m:
            ip = m.group(2)
            counts[ip] = counts.get(ip, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]


# ── geo lookup ─────────────────────────────────────────────────────────

_GEO_CACHE: dict[str, tuple[str, str]] = {}
_GEO_CACHE_MAX = 1024


def get_geo(ip: str, config: Config = None) -> tuple[str, str]:
    if config is None:
        config = Config()
    if ip in _GEO_CACHE:
        return _GEO_CACHE[ip]
    try:
        out = run(f"{shlex.quote(config.GEOIP_BIN)} {shlex.quote(ip)} 2>/dev/null", check=False)
        m = re.search(r':\s*([A-Z]{2}),\s*(.+)', out)
        if m:
            result = (m.group(1).strip(), m.group(2).strip())
        else:
            result = ("??", "")
    except Exception:
        result = ("??", "")
    if len(_GEO_CACHE) >= _GEO_CACHE_MAX:
        _GEO_CACHE.pop(next(iter(_GEO_CACHE)))
    _GEO_CACHE[ip] = result
    return result


def geo_available(config: Config = None) -> bool:
    if config is None:
        config = Config()
    return bool(run(f"which {config.GEOIP_BIN} 2>/dev/null", check=False))


# ── duration helpers ───────────────────────────────────────────────────

_PRESET_SECS = [86400, 432000, 604800, 864000, 1296000, 2592000, -1]


def get_presets(labels: list = None) -> list:
    secs = _PRESET_SECS
    if labels is None:
        labels = ["1 day", "5 days", "7 days", "10 days", "15 days", "30 days", "Permanent"]
    else:
        secs = _PRESET_SECS[:len(labels)]
    return list(zip(labels, secs))


def format_duration(seconds: int) -> str:
    if seconds == -1:
        return "permanente"
    if seconds <= 0:
        return f"{seconds}s"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    parts = []
    if days:
        parts.append(f"{days}g")
    if hours:
        parts.append(f"{hours}h")
    if mins:
        parts.append(f"{mins}m")
    if secs:
        parts.append(f"{secs}s")
    return " ".join(parts) if parts else "0s"


def format_remaining(seconds: int, perm_label: str = "\u221e perm.", expired_label: str = "scaduto") -> str:
    if seconds is None:
        return "\u2014"
    if seconds == -1:
        return perm_label
    if seconds <= 0:
        return expired_label
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    mins = (seconds % 3600) // 60
    if days >= 1:
        return f"{days}g {hours}h" if hours else f"{days}g"
    if hours >= 1:
        return f"{hours}h {mins}m" if mins else f"{hours}h"
    if mins >= 1:
        return f"{mins}m"
    return f"{seconds}s"


def parse_duration(s: str) -> int | None:
    s = s.strip()
    if s.lstrip("-").isdigit():
        v = int(s)
        return v if v == -1 or v > 0 else None
    total = 0
    for val, unit in re.findall(r'(\d+)([dhms])', s.lower()):
        val = int(val)
        if unit == 'd':
            total += val * 86400
        elif unit == 'h':
            total += val * 3600
        elif unit == 'm':
            total += val * 60
        elif unit == 's':
            total += val
    return total if total > 0 else None


def ascii_bar(value: int, max_value: int, width: int = 10) -> str:
    if max_value == 0:
        return "\u2591" * width
    filled = round(value / max_value * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


# ── sorting ────────────────────────────────────────────────────────────

def ip_sort_key(ip: str):
    try:
        return ipaddress.ip_address(ip)
    except ValueError:
        return ipaddress.ip_address("0.0.0.0")


def sort_ips(ips: list, mode: str, stats: dict) -> list:
    if mode == "ip":
        return sorted(ips, key=ip_sort_key)
    elif mode == "date":
        return sorted(ips, key=lambda ip: stats.get(ip, {}).get("ban_time", ""), reverse=True)
    elif mode == "attempts":
        return sorted(ips, key=lambda ip: stats.get(ip, {}).get("total_found", 0), reverse=True)
    return list(ips)


SORT_MODES = ["default", "ip", "date", "attempts"]


# ── i18n ───────────────────────────────────────────────────────────────

STRINGS = {
    "it": {
        "dur_perm": "permanente",
        "rem_perm": "\u221e perm.",
        "rem_expired": "scaduto",
        "sort_default": "originale",
        "sort_ip": "per IP crescente",
        "sort_date": "per data ban (recenti prima)",
        "sort_attempts": "per tentativi (pi\u00f9 aggressivi prima)",
        "p_1d": "1 giorno", "p_5d": "5 giorni", "p_7d": "7 giorni",
        "p_10d": "10 giorni", "p_15d": "15 giorni", "p_30d": "30 giorni",
        "p_perm": "Permanente",
        "cur_bantime": "Ban time attuale",
        "sel_duration": "Seleziona nuova durata:",
        "cur_marker": "\u25c0 attuale",
        "custom_hint": "[c] Custom  (es. 2h30m \u00b7 5d \u00b7 7200 \u00b7 -1 permanente)",
        "cancel": "[Invio] Annulla",
        "prompt_choice": "Scelta",
        "prompt_duration": "Durata",
        "err_format": "Formato non riconosciuto.",
        "err_invalid": "Selezione non valida.",
        "press_enter": "Premi Invio per continuare...",
        "bt_title": "GESTIONE BAN TIME",
        "bt_current": "Ban time corrente",
        "bt_global": "[g] Cambia ban time globale      (vale per i prossimi ban)",
        "bt_ip": "[i] Cambia ban time per un IP    (unban + re-ban con nuova durata)",
        "bt_back": "[Invio] Torna al menu principale",
        "no_banned": "Nessun IP bannato al momento.",
        "banned_title": "IP BANNATI \u2014 seleziona quale:",
        "prompt_ipnum": "Numero o IP (Invio = annulla)",
        "reban_ok": "{} re-bannato per {} ({}s).",
        "reban_err": "Errore nel re-ban di {}.",
        "global_ok": "Ban time globale impostato a {} ({}s).",
        "log_title": "ULTIMI 20 EVENTI:",
        "press_enter_back": "Premi Invio per tornare al menu...",
        "unban_prompt": "Inserisci il numero dell'IP (1-{}) o l'IP completo:",
        "unban_ok": "{} sbannato con successo.",
        "unban_err": "Errore nello sbannare {}.",
        "stat_failed": "Tentativi falliti totali",
        "stat_banned": "IP bannati attualmente",
        "stat_bantime": "Ban time (default)",
        "stat_sort": "Ordinamento",
        "stat_hist": "IP bannati (storico)",
        "col_lastban": "Ultimo ban",
        "col_remaining": "Residuo",
        "col_bar": "Tentativi",
        "menu_r": "[r] Aggiorna",
        "menu_u": "[u] Sbanna un IP",
        "menu_b": "[b] Gestisci ban time",
        "menu_s": "[s] Cambia ordinamento",
        "menu_l": "[l] Ultimi eventi dal log",
        "menu_t": "[t] Statistiche avanzate",
        "menu_j": "[j] Cambia jail",
        "menu_g": "[g] Lingua / Language  \u2192  EN",
        "menu_q": "[q] Esci",
        "stats_title": "STATISTICHE AVANZATE",
        "stats_top5": "TOP 5 IP PI\u00d9 AGGRESSIVI DI SEMPRE  (log corrente)",
        "stats_geo": "DISTRIBUZIONE GEOGRAFICA \u2014 BANNATI ATTUALI",
        "stats_no_data": "Nessun dato disponibile.",
        "geo_unknown": "Sconosciuto",
        "geo_na": "geoiplookup non trovato \u2014 installa: apt install geoip-bin",
    },
    "en": {
        "dur_perm": "permanent",
        "rem_perm": "\u221e perm.",
        "rem_expired": "expired",
        "sort_default": "original",
        "sort_ip": "by IP ascending",
        "sort_date": "by ban date (most recent first)",
        "sort_attempts": "by attempts (most aggressive first)",
        "p_1d": "1 day", "p_5d": "5 days", "p_7d": "7 days",
        "p_10d": "10 days", "p_15d": "15 days", "p_30d": "30 days",
        "p_perm": "Permanent",
        "cur_bantime": "Current ban time",
        "sel_duration": "Select new duration:",
        "cur_marker": "\u25c0 current",
        "custom_hint": "[c] Custom  (e.g. 2h30m \u00b7 5d \u00b7 7200 \u00b7 -1 permanent)",
        "cancel": "[Enter] Cancel",
        "prompt_choice": "Choice",
        "prompt_duration": "Duration",
        "err_format": "Unrecognized format.",
        "err_invalid": "Invalid selection.",
        "press_enter": "Press Enter to continue...",
        "bt_title": "BAN TIME MANAGEMENT",
        "bt_current": "Current ban time",
        "bt_global": "[g] Change global ban time      (applies to future bans)",
        "bt_ip": "[i] Change ban time for an IP   (unban + re-ban with new duration)",
        "bt_back": "[Enter] Back to main menu",
        "no_banned": "No banned IPs at the moment.",
        "banned_title": "BANNED IPs \u2014 select one:",
        "prompt_ipnum": "Number or IP (Enter = cancel)",
        "reban_ok": "{} re-banned for {} ({}s).",
        "reban_err": "Error re-banning {}.",
        "global_ok": "Global ban time set to {} ({}s).",
        "log_title": "LAST 20 EVENTS:",
        "press_enter_back": "Press Enter to go back...",
        "unban_prompt": "Enter the IP number (1-{}) or full IP:",
        "unban_ok": "{} unbanned successfully.",
        "unban_err": "Error unbanning {}.",
        "stat_failed": "Total failed attempts",
        "stat_banned": "Currently banned IPs",
        "stat_bantime": "Ban time (default)",
        "stat_sort": "Sort order",
        "stat_hist": "IPs banned (all time)",
        "col_lastban": "Last ban",
        "col_remaining": "Remaining",
        "col_bar": "Attempts",
        "menu_r": "[r] Refresh",
        "menu_u": "[u] Unban an IP",
        "menu_b": "[b] Manage ban time",
        "menu_s": "[s] Change sort order",
        "menu_l": "[l] Last log events",
        "menu_t": "[t] Advanced statistics",
        "menu_j": "[j] Switch jail",
        "menu_g": "[g] Lingua / Language  \u2192  IT",
        "menu_q": "[q] Quit",
        "stats_title": "ADVANCED STATISTICS",
        "stats_top5": "TOP 5 MOST AGGRESSIVE IPs OF ALL TIME  (current log)",
        "stats_geo": "GEO BREAKDOWN \u2014 CURRENTLY BANNED IPs",
        "stats_no_data": "No data available.",
        "geo_unknown": "Unknown",
        "geo_na": "geoiplookup not found \u2014 install: apt install geoip-bin",
    },
}

_STRINGS_CACHE = STRINGS


def t(key: str, lang: str = "it") -> str:
    return _STRINGS_CACHE.get(lang, {}).get(key, key)
