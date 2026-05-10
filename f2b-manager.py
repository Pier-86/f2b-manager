#!/usr/bin/env python3
import subprocess
import sys
import os
import re
import time
import sqlite3 as _sqlite3
import ipaddress
from datetime import datetime

# ── auto root ────────────────────────────────────────────────────────────────
if os.geteuid() != 0:
    try:
        os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
    except FileNotFoundError:
        print("Errore: sudo non trovato. Esegui lo script come root.")
        sys.exit(1)

# ── i18n ─────────────────────────────────────────────────────────────────────

LANG = "it"

STRINGS = {
    "it": {
        "dur_perm":         "permanente",
        "rem_perm":         "∞ perm.",
        "rem_expired":      "scaduto",
        "sort_default":     "originale",
        "sort_ip":          "per IP crescente",
        "sort_date":        "per data ban (recenti prima)",
        "sort_attempts":    "per tentativi (più aggressivi prima)",
        "p_1d":  "1 giorno",   "p_5d":  "5 giorni",  "p_7d":  "7 giorni",
        "p_10d": "10 giorni",  "p_15d": "15 giorni", "p_30d": "30 giorni",
        "p_perm": "Permanente",
        "cur_bantime":      "Ban time attuale",
        "sel_duration":     "Seleziona nuova durata:",
        "cur_marker":       "◀ attuale",
        "custom_hint":      "[c] Custom  (es. 2h30m · 5d · 7200 · -1 permanente)",
        "cancel":           "[Invio] Annulla",
        "prompt_choice":    "Scelta",
        "prompt_duration":  "Durata",
        "err_format":       "❌ Formato non riconosciuto.",
        "err_invalid":      "❌ Selezione non valida.",
        "press_enter":      "Premi Invio per continuare...",
        "bt_title":         "GESTIONE BAN TIME",
        "bt_current":       "Ban time corrente (jail sshd)",
        "bt_global":        "[g] Cambia ban time globale      (vale per i prossimi ban)",
        "bt_ip":            "[i] Cambia ban time per un IP    (unban + re-ban con nuova durata)",
        "bt_back":          "[Invio] Torna al menu principale",
        "no_banned":        "Nessun IP bannato al momento.",
        "banned_title":     "IP BANNATI — seleziona quale:",
        "prompt_ipnum":     "Numero o IP (Invio = annulla)",
        "reban_ok":         "✅ {} re-bannato per {} ({}s).",
        "reban_err":        "❌ Errore nel re-ban di {}.",
        "global_ok":        "✅ Ban time globale impostato a {} ({}s).",
        "log_title":        "ULTIMI 20 EVENTI:",
        "press_enter_back": "Premi Invio per tornare al menu...",
        "unban_prompt":     "Inserisci il numero dell'IP (1-{}) o l'IP completo:",
        "unban_ok":         "✅ {} sbannato con successo.",
        "unban_err":        "❌ Errore nello sbannare {}.",
        "stat_failed":      "Tentativi falliti totali",
        "stat_banned":      "IP bannati attualmente",
        "stat_bantime":     "Ban time (default)",
        "stat_sort":        "Ordinamento",
        "stat_hist":        "IP bannati (storico)",
        "col_lastban":      "Ultimo ban",
        "col_remaining":    "Residuo",
        "col_bar":          "Tentativi",
        "menu_r":           "[r] Aggiorna",
        "menu_u":           "[u] Sbanna un IP",
        "menu_b":           "[b] Gestisci ban time",
        "menu_s":           "[s] Cambia ordinamento",
        "menu_l":           "[l] Ultimi eventi dal log",
        "menu_t":           "[t] Statistiche avanzate",
        "menu_g":           "[g] Lingua / Language  →  EN",
        "menu_q":           "[q] Esci",
        "stats_title":      "STATISTICHE AVANZATE",
        "stats_top5":       "TOP 5 IP PIÙ AGGRESSIVI DI SEMPRE  (log corrente)",
        "stats_geo":        "DISTRIBUZIONE GEOGRAFICA — BANNATI ATTUALI",
        "stats_no_data":    "Nessun dato disponibile.",
        "geo_unknown":      "Sconosciuto",
        "geo_na":           "geoiplookup non trovato — installa: apt install geoip-bin",
    },
    "en": {
        "dur_perm":         "permanent",
        "rem_perm":         "∞ perm.",
        "rem_expired":      "expired",
        "sort_default":     "original",
        "sort_ip":          "by IP ascending",
        "sort_date":        "by ban date (most recent first)",
        "sort_attempts":    "by attempts (most aggressive first)",
        "p_1d":  "1 day",    "p_5d":  "5 days",   "p_7d":  "7 days",
        "p_10d": "10 days",  "p_15d": "15 days",  "p_30d": "30 days",
        "p_perm": "Permanent",
        "cur_bantime":      "Current ban time",
        "sel_duration":     "Select new duration:",
        "cur_marker":       "◀ current",
        "custom_hint":      "[c] Custom  (e.g. 2h30m · 5d · 7200 · -1 permanent)",
        "cancel":           "[Enter] Cancel",
        "prompt_choice":    "Choice",
        "prompt_duration":  "Duration",
        "err_format":       "❌ Unrecognized format.",
        "err_invalid":      "❌ Invalid selection.",
        "press_enter":      "Press Enter to continue...",
        "bt_title":         "BAN TIME MANAGEMENT",
        "bt_current":       "Current ban time (sshd jail)",
        "bt_global":        "[g] Change global ban time      (applies to future bans)",
        "bt_ip":            "[i] Change ban time for an IP   (unban + re-ban with new duration)",
        "bt_back":          "[Enter] Back to main menu",
        "no_banned":        "No banned IPs at the moment.",
        "banned_title":     "BANNED IPs — select one:",
        "prompt_ipnum":     "Number or IP (Enter = cancel)",
        "reban_ok":         "✅ {} re-banned for {} ({}s).",
        "reban_err":        "❌ Error re-banning {}.",
        "global_ok":        "✅ Global ban time set to {} ({}s).",
        "log_title":        "LAST 20 EVENTS:",
        "press_enter_back": "Press Enter to go back...",
        "unban_prompt":     "Enter the IP number (1-{}) or full IP:",
        "unban_ok":         "✅ {} unbanned successfully.",
        "unban_err":        "❌ Error unbanning {}.",
        "stat_failed":      "Total failed attempts",
        "stat_banned":      "Currently banned IPs",
        "stat_bantime":     "Ban time (default)",
        "stat_sort":        "Sort order",
        "stat_hist":        "IPs banned (all time)",
        "col_lastban":      "Last ban",
        "col_remaining":    "Remaining",
        "col_bar":          "Attempts",
        "menu_r":           "[r] Refresh",
        "menu_u":           "[u] Unban an IP",
        "menu_b":           "[b] Manage ban time",
        "menu_s":           "[s] Change sort order",
        "menu_l":           "[l] Last log events",
        "menu_t":           "[t] Advanced statistics",
        "menu_g":           "[g] Lingua / Language  →  IT",
        "menu_q":           "[q] Quit",
        "stats_title":      "ADVANCED STATISTICS",
        "stats_top5":       "TOP 5 MOST AGGRESSIVE IPs OF ALL TIME  (current log)",
        "stats_geo":        "GEO BREAKDOWN — CURRENTLY BANNED IPs",
        "stats_no_data":    "No data available.",
        "geo_unknown":      "Unknown",
        "geo_na":           "geoiplookup not found — install: apt install geoip-bin",
    },
}

def t(key):
    return STRINGS[LANG][key]

# ── helpers ───────────────────────────────────────────────────────────────────

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip()

# ── fail2ban queries ─────────────────────────────────────────────────────────

def get_status():
    out = run("fail2ban-client status sshd")
    banned_ips, total_failed, total_banned = [], 0, 0
    for line in out.splitlines():
        if "Currently banned" in line:
            total_banned = int(line.split(":")[-1].strip())
        if "Total failed" in line:
            total_failed = int(line.split(":")[-1].strip())
        if "Banned IP list" in line:
            ips = line.split(":")[-1].strip()
            if ips:
                banned_ips = ips.split()
    return banned_ips, total_failed, total_banned

def get_jail_bantime():
    out = run("fail2ban-client get sshd bantime")
    try:
        return int(out)
    except ValueError:
        return 0

def set_jail_bantime(seconds):
    run(f"fail2ban-client set sshd bantime {seconds}")

def unban_ip(ip):
    result = run(f"fail2ban-client set sshd unbanip {ip}")
    return "1" in result or result == ip

def reban_ip(ip, seconds):
    original = get_jail_bantime()
    r_unban  = run(f"fail2ban-client set sshd unbanip {ip}")
    if "1" not in r_unban:
        return False
    run(f"fail2ban-client set sshd bantime {seconds}")
    r_ban = run(f"fail2ban-client set sshd banip {ip}")
    run(f"fail2ban-client set sshd bantime {original}")
    return "1" in r_ban

F2B_DB = "/var/lib/fail2ban/fail2ban.sqlite3"

def get_remaining_bantimes(ips):
    if not ips:
        return {}
    ips_set = set(ips)
    now     = time.time()
    result  = {}
    try:
        conn = _sqlite3.connect(F2B_DB)
        rows = conn.execute(
            "SELECT ip, timeofban, bantime FROM bans WHERE jail='sshd'"
        ).fetchall()
        conn.close()
        for ip, timeofban, bantime in rows:
            if ip not in ips_set:
                continue
            bantime = int(bantime)
            if bantime == -1:
                result[ip] = -1
            else:
                result[ip] = max(0, int((timeofban + bantime) - now))
    except Exception:
        pass
    return result

def get_historical_count():
    try:
        conn = _sqlite3.connect(F2B_DB)
        row  = conn.execute("SELECT COUNT(DISTINCT ip) FROM bans WHERE jail='sshd'").fetchone()
        conn.close()
        return row[0] if row else 0
    except Exception:
        return 0

# ── log parsing ──────────────────────────────────────────────────────────────

_BAN_RE   = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[sshd\] Ban (\S+)$')
_FOUND_RE = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[sshd\] Found (\S+)')

def get_ip_stats(ips):
    if not ips:
        return {}
    ips_set = set(ips)
    out = run("grep -E '\\[sshd\\].*(Ban |Found )' /var/log/fail2ban.log 2>/dev/null")
    events = {ip: [] for ip in ips}
    for line in out.splitlines():
        m = _BAN_RE.match(line)
        if m:
            ts, ip = m.group(1), m.group(2)
            if ip in ips_set:
                events[ip].append((ts, "ban"))
            continue
        m = _FOUND_RE.match(line)
        if m:
            ts, ip = m.group(1), m.group(2)
            if ip in ips_set:
                events[ip].append((ts, "found"))
    result = {}
    for ip in ips:
        ev = events[ip]
        total_found = sum(1 for _, kind in ev if kind == "found")
        last_ban_ts = None
        for ts, kind in ev:
            if kind == "ban":
                last_ban_ts = ts
        found_after_ban = 0
        if last_ban_ts:
            found_after_ban = sum(1 for ts, kind in ev if kind == "found" and ts > last_ban_ts)
        result[ip] = {
            "ban_time":        last_ban_ts or "—",
            "total_found":     total_found,
            "found_after_ban": found_after_ban,
        }
    return result

def get_top_ips(n=5):
    out = run("grep '\\[sshd\\] Found' /var/log/fail2ban.log 2>/dev/null")
    counts = {}
    for line in out.splitlines():
        m = _FOUND_RE.match(line)
        if m:
            ip = m.group(2)
            counts[ip] = counts.get(ip, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]

# ── geo lookup ───────────────────────────────────────────────────────────────

_GEO_CACHE = {}
_GEO_OK    = None

def _geo_available():
    global _GEO_OK
    if _GEO_OK is None:
        _GEO_OK = bool(run("which geoiplookup 2>/dev/null"))
    return _GEO_OK

def get_geo(ip):
    """Returns (country_code, country_name). Falls back to ('??', '') if unavailable."""
    if ip in _GEO_CACHE:
        return _GEO_CACHE[ip]
    if not _geo_available():
        _GEO_CACHE[ip] = ("??", "")
        return ("??", "")
    out = run(f"geoiplookup {ip} 2>/dev/null")
    m = re.search(r':\s*([A-Z]{2}),\s*(.+)', out)
    result = (m.group(1).strip(), m.group(2).strip()) if m else ("??", "")
    _GEO_CACHE[ip] = result
    return result

# ── duration helpers ─────────────────────────────────────────────────────────

_PRESET_KEYS = ["p_1d", "p_5d", "p_7d", "p_10d", "p_15d", "p_30d", "p_perm"]
_PRESET_SECS = [86400, 432000, 604800, 864000, 1296000, 2592000, -1]

def get_presets():
    return list(zip([t(k) for k in _PRESET_KEYS], _PRESET_SECS))

def format_duration(seconds):
    if seconds == -1:
        return t("dur_perm")
    if seconds <= 0:
        return f"{seconds}s"
    days  = seconds // 86400
    hours = (seconds % 86400) // 3600
    mins  = (seconds % 3600) // 60
    secs  = seconds % 60
    parts = []
    if days:  parts.append(f"{days}g")
    if hours: parts.append(f"{hours}h")
    if mins:  parts.append(f"{mins}m")
    if secs:  parts.append(f"{secs}s")
    return " ".join(parts) if parts else "0s"

def format_remaining(seconds):
    if seconds is None:
        return "—"
    if seconds == -1:
        return t("rem_perm")
    if seconds <= 0:
        return t("rem_expired")
    days  = seconds // 86400
    hours = (seconds % 86400) // 3600
    mins  = (seconds % 3600) // 60
    if days >= 1:
        return f"{days}g {hours}h" if hours else f"{days}g"
    if hours >= 1:
        return f"{hours}h {mins}m" if mins else f"{hours}h"
    if mins >= 1:
        return f"{mins}m"
    return f"{seconds}s"

def parse_duration(s):
    s = s.strip()
    if s.lstrip("-").isdigit():
        v = int(s)
        return v if v == -1 or v > 0 else None
    total = 0
    for val, unit in re.findall(r'(\d+)([dhms])', s.lower()):
        val = int(val)
        if   unit == 'd': total += val * 86400
        elif unit == 'h': total += val * 3600
        elif unit == 'm': total += val * 60
        elif unit == 's': total += val
    return total if total > 0 else None

def ascii_bar(value, max_value, width=10):
    if max_value == 0:
        return "░" * width
    filled = round(value / max_value * width)
    return "█" * filled + "░" * (width - filled)

# ── sorting ──────────────────────────────────────────────────────────────────

def ip_sort_key(ip):
    try:
        return ipaddress.ip_address(ip)
    except ValueError:
        return ipaddress.ip_address("0.0.0.0")

def sort_ips(ips, mode, stats):
    if mode == "ip":
        return sorted(ips, key=ip_sort_key)
    elif mode == "date":
        return sorted(ips, key=lambda ip: stats.get(ip, {}).get("ban_time", ""), reverse=True)
    elif mode == "attempts":
        return sorted(ips, key=lambda ip: stats.get(ip, {}).get("total_found", 0), reverse=True)
    return list(ips)

SORT_MODES = ["default", "ip", "date", "attempts"]

def sort_label(mode):
    return t(f"sort_{mode}")

# ── UI helpers ───────────────────────────────────────────────────────────────

def clear():
    os.system("clear")

def header():
    tag   = f"[{LANG.upper()}]"
    title = "          FAIL2BAN MANAGER — SSH Protection"
    line  = title + " " * (78 - len(title) - len(tag)) + tag
    print("=" * 78)
    print(line)
    print("=" * 78)
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 78)

# ── pick duration ─────────────────────────────────────────────────────────────

def pick_duration():
    presets = get_presets()
    current = get_jail_bantime()
    clear()
    header()
    print(f"\n  {t('cur_bantime')}: {format_duration(current)} ({current}s)\n")
    print(f"  {t('sel_duration')}\n")
    for i, (label, secs) in enumerate(presets, 1):
        marker = f"  {t('cur_marker')}" if secs == current else ""
        print(f"  [{i}] {label:<14}  {format_duration(secs)}{marker}")
    print(f"  {t('custom_hint')}")
    print(f"  {t('cancel')}")
    print()
    scelta = input(f"  {t('prompt_choice')}: ").strip().lower()
    if scelta == "":
        return None
    if scelta == "c":
        val  = input(f"  {t('prompt_duration')}: ").strip()
        secs = parse_duration(val)
        if secs is None:
            print(f"  {t('err_format')}")
            input(f"  {t('press_enter')}")
            return None
        return secs
    if scelta.isdigit():
        idx = int(scelta) - 1
        if 0 <= idx < len(presets):
            return presets[idx][1]
    print(f"  {t('err_invalid')}")
    input(f"  {t('press_enter')}")
    return None

# ── bantime menu ──────────────────────────────────────────────────────────────

def bantime_menu(sorted_ips):
    while True:
        current = get_jail_bantime()
        clear()
        header()
        print(f"\n  {t('bt_title')}\n")
        print(f"  {t('bt_current')}: {format_duration(current)} ({current}s)\n")
        print(f"  {t('bt_global')}")
        print(f"  {t('bt_ip')}")
        print(f"  {t('bt_back')}")
        print()
        scelta = input(f"  {t('prompt_choice')}: ").strip().lower()

        if scelta == "":
            break

        elif scelta == "g":
            secs = pick_duration()
            if secs is not None:
                set_jail_bantime(secs)
                clear()
                header()
                print(f"\n  {t('global_ok').format(format_duration(secs), secs)}")
                input(f"  {t('press_enter')}")

        elif scelta == "i":
            if not sorted_ips:
                print(f"\n  {t('no_banned')}")
                input(f"  {t('press_enter')}")
                continue
            clear()
            header()
            print(f"\n  {t('banned_title')}\n")
            for i, ip in enumerate(sorted_ips, 1):
                print(f"  [{i:<2}]  {ip}")
            print()
            val = input(f"  {t('prompt_ipnum')}: ").strip()
            if val == "":
                continue
            ip_target = None
            if val.isdigit():
                idx = int(val) - 1
                if 0 <= idx < len(sorted_ips):
                    ip_target = sorted_ips[idx]
            elif val in sorted_ips:
                ip_target = val
            if not ip_target:
                print(f"  {t('err_invalid')}")
                input(f"  {t('press_enter')}")
                continue
            secs = pick_duration()
            if secs is not None:
                ok = reban_ip(ip_target, secs)
                clear()
                header()
                if ok:
                    print(f"\n  {t('reban_ok').format(ip_target, format_duration(secs), secs)}")
                else:
                    print(f"\n  {t('reban_err').format(ip_target)}")
                input(f"  {t('press_enter')}")

# ── stats screen ──────────────────────────────────────────────────────────────

def stats_screen(banned_ips):
    clear()
    header()
    print(f"\n  ── {t('stats_title')} ──\n")

    # contatore storico
    hist = get_historical_count()
    print(f"  {t('stat_hist')}: {hist}\n")

    # top 5
    print(f"  {t('stats_top5')}")
    print("  " + "─" * 62)
    top = get_top_ips(5)
    if top:
        max_c = top[0][1]
        for ip, count in top:
            cc, name = get_geo(ip)
            label = name if name else t("geo_unknown")
            bar   = ascii_bar(count, max_c, 20)
            print(f"  {ip:<18}  {cc:<2}  {bar}  {count:>5}  {label}")
    else:
        print(f"  {t('stats_no_data')}")
    print()

    # distribuzione geografica
    print(f"  {t('stats_geo')}")
    print("  " + "─" * 62)
    if not _geo_available():
        print(f"  {t('geo_na')}")
    elif banned_ips:
        counts = {}
        names  = {}
        for ip in banned_ips:
            cc, name = get_geo(ip)
            counts[cc] = counts.get(cc, 0) + 1
            if name:
                names[cc] = name
        sorted_cc = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        max_c = sorted_cc[0][1]
        for cc, count in sorted_cc:
            name = names.get(cc, t("geo_unknown"))
            bar  = ascii_bar(count, max_c, 20)
            pct  = round(count / len(banned_ips) * 100)
            print(f"  {cc:<4}  {name:<28}  {bar}  {count:>3}  ({pct}%)")
    else:
        print(f"  {t('no_banned')}")

    print()
    input(f"  {t('press_enter_back')}")

# ── main loop ────────────────────────────────────────────────────────────────

def main():
    global LANG
    sort_idx = 0

    while True:
        clear()
        header()

        banned_ips, total_failed, total_banned = get_status()
        stats      = get_ip_stats(banned_ips)
        remaining  = get_remaining_bantimes(banned_ips)
        hist_count = get_historical_count()
        sort_mode  = SORT_MODES[sort_idx]
        sorted_ips = sort_ips(banned_ips, sort_mode, stats)
        current_bt = get_jail_bantime()

        stat_keys = ("stat_failed", "stat_banned", "stat_hist", "stat_bantime", "stat_sort")
        w = max(len(t(k)) for k in stat_keys)
        print(f"\n  {t('stat_failed'):<{w}} : {total_failed}")
        print(f"  {t('stat_banned'):<{w}} : {total_banned}")
        print(f"  {t('stat_hist'):<{w}} : {hist_count}")
        print(f"  {t('stat_bantime'):<{w}} : {format_duration(current_bt)} ({current_bt}s)")
        print(f"  {t('stat_sort'):<{w}} : {sort_label(sort_mode)}")
        print()

        if not sorted_ips:
            print(f"  {t('no_banned')}\n")
        else:
            max_tot = max((stats.get(ip, {}).get("total_found", 0) for ip in sorted_ips), default=1) or 1
            col_lb  = t("col_lastban")
            col_rem = t("col_remaining")
            col_bar = t("col_bar")
            # columns: # IP CC LastBan Remaining Tot Bar(10)
            # widths:  4  15  2   19       9      3   10  → 76 chars + 2 indent = 78
            print(f"  {'#':<4}  {'IP':<15}  {'CC':<2}  {col_lb:<19}  {col_rem:<9}  {'Tot':>3}  {col_bar:<10}")
            print("  " + "─" * 74)
            for i, ip in enumerate(sorted_ips, 1):
                s    = stats.get(ip, {})
                bt   = s.get("ban_time", "—")
                tot  = s.get("total_found", 0)
                aft  = s.get("found_after_ban", 0)
                rem  = format_remaining(remaining.get(ip))
                bar  = ascii_bar(tot, max_tot, 10)
                cc, _ = get_geo(ip)
                post = f"  🔴 +{aft}" if aft > 0 else ""
                print(f"  [{i:<2}]  {ip:<15}  {cc:<2}  {bt:<19}  {rem:<9}  {tot:>3}  {bar}{post}")
            print()

        print(f"  {t('menu_r')}")
        print(f"  {t('menu_u')}")
        print(f"  {t('menu_b')}")
        print(f"  {t('menu_s')}")
        print(f"  {t('menu_l')}")
        print(f"  {t('menu_t')}")
        print(f"  {t('menu_g')}")
        print(f"  {t('menu_q')}")
        print()

        scelta = input(f"  {t('prompt_choice')}: ").strip().lower()

        if scelta == "q":
            print()
            sys.exit(0)

        elif scelta == "r":
            continue

        elif scelta == "s":
            sort_idx = (sort_idx + 1) % len(SORT_MODES)
            continue

        elif scelta == "g":
            LANG = "en" if LANG == "it" else "it"
            continue

        elif scelta == "b":
            bantime_menu(sorted_ips)

        elif scelta == "t":
            stats_screen(banned_ips)

        elif scelta == "l":
            clear()
            header()
            print(f"\n  {t('log_title')}\n")
            log = run("grep -E 'Ban|Unban|Found' /var/log/fail2ban.log | tail -20")
            for line in log.splitlines():
                if "Ban " in line and "Unban" not in line:
                    print(f"  🔴 {line}")
                elif "Unban" in line:
                    print(f"  🟢 {line}")
                else:
                    print(f"  ⚪ {line}")
            print()
            input(f"  {t('press_enter_back')}")

        elif scelta == "u":
            if not sorted_ips:
                print(f"\n  {t('no_banned')}")
                input(f"  {t('press_enter')}")
                continue
            print(f"\n  {t('unban_prompt').format(len(sorted_ips))}")
            val = input("  > ").strip()
            ip_to_unban = None
            if val.isdigit():
                idx = int(val) - 1
                if 0 <= idx < len(sorted_ips):
                    ip_to_unban = sorted_ips[idx]
            elif val in sorted_ips:
                ip_to_unban = val
            if ip_to_unban:
                if unban_ip(ip_to_unban):
                    print(f"\n  {t('unban_ok').format(ip_to_unban)}")
                else:
                    print(f"\n  {t('unban_err').format(ip_to_unban)}")
            else:
                print(f"\n  {t('err_invalid')}")
            input(f"  {t('press_enter')}")

        else:
            continue

if __name__ == "__main__":
    main()
