#!/usr/bin/env python3
import os
import sys
from datetime import datetime

if os.geteuid() != 0:
    try:
        os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
    except FileNotFoundError:
        print("Errore: sudo non trovato. Esegui lo script come root.")
        sys.exit(1)

from f2b_core import (
    Config, F2BError, get_jail_status, get_jail_bantime, set_jail_bantime,
    unban_ip, reban_ip, get_remaining_bantimes, get_historical_count,
    get_ip_stats, get_top_ips, get_geo, geo_available, get_available_jails,
    format_duration, format_remaining, parse_duration, ascii_bar,
    sort_ips, SORT_MODES, t as _t,
)

LANG = os.environ.get("F2B_LANG", "it")
if LANG not in ("it", "en"):
    LANG = "it"
config = Config()
jails_cache = []


def t(key):
    return _t(key, LANG)


def clear():
    os.system("clear")


def header():
    tag = f"[{LANG.upper()}]"
    jail_tag = f"[{config.ACTIVE_JAIL}]"
    title = f"          FAIL2BAN MANAGER \u2014 {config.ACTIVE_JAIL}"
    line = title + " " * (58 - len(title) - len(jail_tag)) + jail_tag + " " * 4 + tag
    print("=" * 78)
    print(line)
    print("=" * 78)
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 78)


def pick_duration(jail=None):
    j = jail or config.ACTIVE_JAIL
    presets = list(zip(
        [t(f"p_{k}") for k in ["1d", "5d", "7d", "10d", "15d", "30d", "perm"]],
        [86400, 432000, 604800, 864000, 1296000, 2592000, -1]
    ))
    current = get_jail_bantime(j, config)
    clear()
    header()
    print(f"\n  {t('cur_bantime')} [{j}]: {format_duration(current)} ({current}s)\n")
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
        val = input(f"  {t('prompt_duration')}: ").strip()
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


def bantime_menu(sorted_ips, jail=None):
    j = jail or config.ACTIVE_JAIL
    while True:
        current = get_jail_bantime(j, config)
        clear()
        header()
        print(f"\n  {t('bt_title')} \u2014 [{j}]\n")
        print(f"  {t('bt_current')}: {format_duration(current)} ({current}s)\n")
        print(f"  {t('bt_global')}")
        print(f"  {t('bt_ip')}")
        print(f"  {t('bt_back')}")
        print()
        scelta = input(f"  {t('prompt_choice')}: ").strip().lower()
        if scelta == "":
            break
        elif scelta == "g":
            secs = pick_duration(j)
            if secs is not None:
                set_jail_bantime(secs, j, config)
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
            secs = pick_duration(j)
            if secs is not None:
                ok = reban_ip(ip_target, secs, j, config)
                clear()
                header()
                if ok:
                    print(f"\n  {t('reban_ok').format(ip_target, format_duration(secs), secs)}")
                else:
                    print(f"\n  {t('reban_err').format(ip_target)}")
                input(f"  {t('press_enter')}")


def stats_screen(banned_ips, jail=None):
    j = jail or config.ACTIVE_JAIL
    clear()
    header()
    print(f"\n  \u2014\u2014 {t('stats_title')} \u2014\u2014\n")
    hist = get_historical_count(j, config)
    print(f"  {t('stat_hist')}: {hist}\n")
    print(f"  {t('stats_top5')}  [{j}]")
    print("  " + "\u2500" * 62)
    top = get_top_ips(5, j, config)
    if top:
        max_c = top[0][1]
        for ip, count in top:
            cc, name = get_geo(ip, config)
            label = name if name else t("geo_unknown")
            bar = ascii_bar(count, max_c, 20)
            print(f"  {ip:<18}  {cc:<2}  {bar}  {count:>5}  {label}")
    else:
        print(f"  {t('stats_no_data')}")
    print()
    print(f"  {t('stats_geo')}")
    print("  " + "\u2500" * 62)
    if not geo_available(config):
        print(f"  {t('geo_na')}")
    elif banned_ips:
        counts = {}
        names = {}
        for ip in banned_ips:
            cc, name = get_geo(ip, config)
            counts[cc] = counts.get(cc, 0) + 1
            if name:
                names[cc] = name
        sorted_cc = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        max_c = sorted_cc[0][1]
        for cc, count in sorted_cc:
            name = names.get(cc, t("geo_unknown"))
            bar = ascii_bar(count, max_c, 20)
            pct = round(count / len(banned_ips) * 100)
            print(f"  {cc:<4}  {name:<28}  {bar}  {count:>3}  ({pct}%)")
    else:
        print(f"  {t('no_banned')}")
    print()
    input(f"  {t('press_enter_back')}")


def main():
    global LANG, jails_cache
    sort_idx = 0
    jail_idx = 0

    jails_cache = get_available_jails()
    if jails_cache:
        config.ACTIVE_JAIL = jails_cache[0]["jail"]

    while True:
        clear()
        header()

        try:
            status = get_jail_status(config.ACTIVE_JAIL, config)
        except F2BError as e:
            print(f"\n  Errore: fail2ban jail '{config.ACTIVE_JAIL}' non raggiungibile \u2014 {e}")
            print(f"  Premi [j] per cambiare jail o [Invio] per riprovare")
            scelta = input(f"  {t('prompt_choice')}: ").strip().lower()
            if scelta == "j":
                jails_cache = get_available_jails()
                if jails_cache:
                    jail_idx = (jail_idx + 1) % len(jails_cache)
                    config.ACTIVE_JAIL = jails_cache[jail_idx]["jail"]
            continue

        banned_ips = status["banned_ips"]
        total_failed = status["total_failed"]
        total_banned = status["total_banned"]
        stats = get_ip_stats(banned_ips, config.ACTIVE_JAIL, config)
        remaining = get_remaining_bantimes(banned_ips, config.ACTIVE_JAIL, config)
        hist_count = get_historical_count(config.ACTIVE_JAIL, config)
        sort_mode = SORT_MODES[sort_idx]
        sorted_ips = sort_ips(banned_ips, sort_mode, stats)
        current_bt = get_jail_bantime(config.ACTIVE_JAIL, config)

        stat_keys = ("stat_failed", "stat_banned", "stat_hist", "stat_bantime", "stat_sort")
        w = max(len(t(k)) for k in stat_keys)
        print(f"\n  {t('stat_failed'):<{w}} : {total_failed}")
        print(f"  {t('stat_banned'):<{w}} : {total_banned}")
        print(f"  {t('stat_hist'):<{w}} : {hist_count}")
        print(f"  {t('stat_bantime'):<{w}} : {format_duration(current_bt)} ({current_bt}s)")
        print(f"  {t('stat_sort'):<{w}} : {t(f'sort_{sort_mode}')}")
        print()

        if not sorted_ips:
            print(f"  {t('no_banned')}\n")
        else:
            max_tot = max((stats.get(ip, {}).get("total_found", 0) for ip in sorted_ips), default=1) or 1
            col_lb = t("col_lastban")
            col_rem = t("col_remaining")
            col_bar = t("col_bar")
            print(f"  {'#':<4}  {'IP':<15}  {'CC':<2}  {col_lb:<19}  {col_rem:<9}  {'Tot':>3}  {col_bar:<10}")
            print("  " + "\u2500" * 74)
            for i, ip in enumerate(sorted_ips, 1):
                s = stats.get(ip, {})
                bt = s.get("ban_time", "\u2014")
                tot = s.get("total_found", 0)
                aft = s.get("found_after_ban", 0)
                rem = format_remaining(remaining.get(ip), t("rem_perm"), t("rem_expired"))
                bar = ascii_bar(tot, max_tot, 10)
                cc, _ = get_geo(ip, config)
                post = f"  \U0001f534 +{aft}" if aft > 0 else ""
                print(f"  [{i:<2}]  {ip:<15}  {cc:<2}  {bt:<19}  {rem:<9}  {tot:>3}  {bar}{post}")
            print()

        print(f"  {t('menu_r')}")
        if len(jails_cache) > 1:
            print(f"  [j] Cambia jail  ({config.ACTIVE_JAIL})")
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
        elif scelta == "j":
            jails_cache = get_available_jails()
            if jails_cache:
                jail_idx = (jail_idx + 1) % len(jails_cache)
                config.ACTIVE_JAIL = jails_cache[jail_idx]["jail"]
            continue
        elif scelta == "b":
            bantime_menu(sorted_ips, config.ACTIVE_JAIL)
        elif scelta == "t":
            stats_screen(banned_ips, config.ACTIVE_JAIL)
        elif scelta == "l":
            clear()
            header()
            print(f"\n  {t('log_title')}  [{config.ACTIVE_JAIL}]\n")
            from f2b_core import run as _run
            log = _run(f"grep -E '\\[{config.ACTIVE_JAIL}\\] (Ban|Unban|Found)' {config.F2B_LOG} 2>/dev/null | tail -20", check=False)
            for line in log.splitlines():
                if "Ban " in line and "Unban" not in line:
                    print(f"  \U0001f534 {line}")
                elif "Unban" in line:
                    print(f"  \U0001f7e2 {line}")
                else:
                    print(f"  \u26aa {line}")
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
                try:
                    if unban_ip(ip_to_unban, config.ACTIVE_JAIL, config):
                        print(f"\n  {t('unban_ok').format(ip_to_unban)}")
                    else:
                        print(f"\n  {t('unban_err').format(ip_to_unban)}")
                except F2BError as e:
                    print(f"\n  Errore: {e}")
            else:
                print(f"\n  {t('err_invalid')}")
            input(f"  {t('press_enter')}")
        else:
            continue


if __name__ == "__main__":
    main()
