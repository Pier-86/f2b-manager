#!/usr/bin/env python3
import subprocess
import sys
import os
import re
import time
import sqlite3 as _sqlite3
import ipaddress
from datetime import datetime

# ── auto-elevazione root ──────────────────────────────────────────────────────
# Se non siamo già root, ri-eseguiamo lo stesso script con sudo.
# L'utente digita solo:  python3 f2b-manager.py
if os.geteuid() != 0:
    try:
        os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
    except FileNotFoundError:
        print("Errore: sudo non trovato. Esegui lo script come root.")
        sys.exit(1)

# ── helpers ───────────────────────────────────────────────────────────────────

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip()

# ── fail2ban queries ─────────────────────────────────────────────────────────

def get_status():
    out = run("fail2ban-client status sshd")
    banned_ips = []
    total_failed = 0
    total_banned = 0
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
    """Unban, imposta nuovo bantime, re-ban, ripristina bantime originale.
    Restituisce True se il re-ban è andato a buon fine."""
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
    """{ip: secondi_rimanenti}  (-1 = permanente, None = non trovato)"""
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
        total_found = sum(1 for _, t in ev if t == "found")
        last_ban_ts = None
        for ts, t in ev:
            if t == "ban":
                last_ban_ts = ts
        found_after_ban = 0
        if last_ban_ts:
            found_after_ban = sum(1 for ts, t in ev if t == "found" and ts > last_ban_ts)
        result[ip] = {
            "ban_time":        last_ban_ts or "—",
            "total_found":     total_found,
            "found_after_ban": found_after_ban,
        }
    return result

# ── duration helpers ─────────────────────────────────────────────────────────

PRESETS = [
    ("1 giorno",    86400),
    ("5 giorni",   432000),
    ("7 giorni",   604800),
    ("10 giorni",  864000),
    ("15 giorni", 1296000),
    ("30 giorni", 2592000),
    ("Permanente",     -1),
]

def format_duration(seconds):
    if seconds == -1:
        return "permanente"
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
        return "∞ perm."
    if seconds <= 0:
        return "scaduto"
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

SORT_MODES  = ["default", "ip", "date", "attempts"]
SORT_LABELS = {
    "default":  "originale",
    "ip":       "per IP crescente",
    "date":     "per data ban (recenti prima)",
    "attempts": "per tentativi (più aggressivi prima)",
}

# ── UI helpers ───────────────────────────────────────────────────────────────

def clear():
    os.system("clear")

def header():
    print("=" * 78)
    print("          FAIL2BAN MANAGER — SSH Protection")
    print("=" * 78)
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 78)

# ── bantime sub-menu ─────────────────────────────────────────────────────────

def pick_duration():
    current = get_jail_bantime()
    clear()
    header()
    print(f"\n  Ban time attuale: {format_duration(current)} ({current}s)\n")
    print("  Seleziona nuova durata:\n")
    for i, (label, secs) in enumerate(PRESETS, 1):
        marker = " ◀ attuale" if secs == current else ""
        print(f"  [{i}] {label:<14}  {format_duration(secs)}{marker}")
    print(f"  [c] Custom  (es. 2h30m · 5d · 7200 · -1 permanente)")
    print(f"  [Invio] Annulla")
    print()
    scelta = input("  Scelta: ").strip().lower()
    if scelta == "":
        return None
    if scelta == "c":
        val  = input("  Durata: ").strip()
        secs = parse_duration(val)
        if secs is None:
            print("  ❌ Formato non riconosciuto.")
            input("  Premi Invio per continuare...")
            return None
        return secs
    if scelta.isdigit():
        idx = int(scelta) - 1
        if 0 <= idx < len(PRESETS):
            return PRESETS[idx][1]
    print("  ❌ Selezione non valida.")
    input("  Premi Invio per continuare...")
    return None

def bantime_menu(sorted_ips):
    while True:
        current = get_jail_bantime()
        clear()
        header()
        print(f"\n  GESTIONE BAN TIME\n")
        print(f"  Ban time corrente (jail sshd): {format_duration(current)} ({current}s)\n")
        print("  [g] Cambia ban time globale      (vale per i prossimi ban)")
        print("  [i] Cambia ban time per un IP    (unban + re-ban con nuova durata)")
        print("  [Invio] Torna al menu principale")
        print()
        scelta = input("  Scelta: ").strip().lower()

        if scelta == "":
            break

        elif scelta == "g":
            secs = pick_duration()
            if secs is not None:
                set_jail_bantime(secs)
                clear()
                header()
                print(f"\n  ✅ Ban time globale impostato a {format_duration(secs)} ({secs}s).")
                input("  Premi Invio per continuare...")

        elif scelta == "i":
            if not sorted_ips:
                print("\n  Nessun IP bannato al momento.")
                input("  Premi Invio per continuare...")
                continue
            clear()
            header()
            print("\n  IP BANNATI — seleziona quale:\n")
            for i, ip in enumerate(sorted_ips, 1):
                print(f"  [{i:<2}]  {ip}")
            print()
            val = input("  Numero o IP (Invio = annulla): ").strip()
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
                print("  ❌ Selezione non valida.")
                input("  Premi Invio per continuare...")
                continue
            secs = pick_duration()
            if secs is not None:
                ok = reban_ip(ip_target, secs)
                clear()
                header()
                if ok:
                    print(f"\n  ✅ {ip_target} re-bannato per {format_duration(secs)} ({secs}s).")
                else:
                    print(f"\n  ❌ Errore nel re-ban di {ip_target}.")
                input("  Premi Invio per continuare...")

# ── main loop ────────────────────────────────────────────────────────────────

def main():
    sort_idx = 0

    while True:
        clear()
        header()

        banned_ips, total_failed, total_banned = get_status()
        stats      = get_ip_stats(banned_ips)
        remaining  = get_remaining_bantimes(banned_ips)
        sort_mode  = SORT_MODES[sort_idx]
        sorted_ips = sort_ips(banned_ips, sort_mode, stats)
        current_bt = get_jail_bantime()

        print(f"\n  Tentativi falliti totali : {total_failed}")
        print(f"  IP bannati attualmente   : {total_banned}")
        print(f"  Ban time (default)       : {format_duration(current_bt)} ({current_bt}s)")
        print(f"  Ordinamento              : {SORT_LABELS[sort_mode]}")
        print()

        if not sorted_ips:
            print("  Nessun IP bannato al momento.\n")
        else:
            print(f"  {'#':<4}  {'IP':<18}  {'Ultimo ban':<19}  {'Residuo':<10}  {'Tot':>4}  Attivi")
            print("  " + "-" * 70)
            for i, ip in enumerate(sorted_ips, 1):
                s    = stats.get(ip, {})
                bt   = s.get("ban_time", "—")
                tot  = s.get("total_found", 0)
                aft  = s.get("found_after_ban", 0)
                rem  = format_remaining(remaining.get(ip))
                post = f"🔴 +{aft}" if aft > 0 else ""
                print(f"  [{i:<2}]  {ip:<18}  {bt:<19}  {rem:<10}  {tot:>4}  {post}")
            print()

        print("  [r] Aggiorna")
        print("  [u] Sbanna un IP")
        print("  [b] Gestisci ban time")
        print("  [s] Cambia ordinamento")
        print("  [l] Ultimi eventi dal log")
        print("  [q] Esci")
        print()

        scelta = input("  Scelta: ").strip().lower()

        if scelta == "q":
            print()
            sys.exit(0)

        elif scelta == "r":
            continue

        elif scelta == "s":
            sort_idx = (sort_idx + 1) % len(SORT_MODES)
            continue

        elif scelta == "b":
            bantime_menu(sorted_ips)

        elif scelta == "l":
            clear()
            header()
            print("\n  ULTIMI 20 EVENTI:\n")
            log = run("grep -E 'Ban|Unban|Found' /var/log/fail2ban.log | tail -20")
            for line in log.splitlines():
                if "Ban " in line and "Unban" not in line:
                    print(f"  🔴 {line}")
                elif "Unban" in line:
                    print(f"  🟢 {line}")
                else:
                    print(f"  ⚪ {line}")
            print()
            input("  Premi Invio per tornare al menu...")

        elif scelta == "u":
            if not sorted_ips:
                print("\n  Nessun IP da sbannare.")
                input("  Premi Invio per continuare...")
                continue
            print(f"\n  Inserisci il numero dell'IP (1-{len(sorted_ips)}) o l'IP completo:")
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
                    print(f"\n  ✅ {ip_to_unban} sbannato con successo.")
                else:
                    print(f"\n  ❌ Errore nello sbannare {ip_to_unban}.")
            else:
                print("\n  ❌ Selezione non valida.")
            input("  Premi Invio per continuare...")

        else:
            continue

if __name__ == "__main__":
    main()
