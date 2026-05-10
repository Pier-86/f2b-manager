<div align="center">

# 🛡️ f2b-manager

### Fail2ban SSH Manager — Terminal User Interface

[![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?logo=linux&logoColor=black)](https://kernel.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)
[![Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)]()
[![Language](https://img.shields.io/badge/Language-IT%20%7C%20EN-8b5cf6)]()

<br>

*Gestisci fail2ban dal terminale — senza ricordare un solo comando.*
*Manage fail2ban from the terminal — without memorizing a single command.*

<br>

**🇮🇹 [Italiano](#-italiano) · 🇬🇧 [English](#-english)**

</div>

---

## 🇮🇹 Italiano

### Cos'è f2b-manager?

`f2b-manager` è uno strumento TUI (**Terminal User Interface**) scritto in Python puro che ti permette di gestire **fail2ban** in modo semplice, visivo e immediato — direttamente dal terminale del tuo server.

Nessuna dipendenza esterna. Nessun framework. Avvialo e hai tutto sotto controllo.

---

### ✨ Funzionalità

| | Funzione |
|---|---|
| 🌍 | **Geolocalizzazione** — paese di origine di ogni IP nella tabella (`CC`) |
| 📊 | **Grafico a barre ASCII** — aggressività relativa di ogni IP, visiva e immediata |
| 📈 | **Contatore storico** — quanti IP distinti sono stati bannati dall'inizio (SQLite) |
| 🏆 | **Top 5 di sempre** — gli IP più aggressivi in assoluto, con barre e paese |
| 🗺️ | **Mappa geografica** — distribuzione degli attacchi per paese con percentuali |
| ⏱️ | **Tempo residuo preciso** — letto dal database SQLite di fail2ban, al secondo |
| 🔧 | **Gestione ban time** — modifica globale o per singolo IP (unban + re-ban) |
| 🔢 | **Preset pronti** — 1g, 5g, 7g, 10g, 15g, 30g, permanente · oppure input custom |
| ↕️ | **Ordinamento flessibile** — IP, data ban, numero di tentativi |
| 🌐 | **Multilingua IT/EN** — cambia lingua al volo con `[g]` |
| 🔐 | **Auto root** — si ri-esegue con `sudo` automaticamente |
| 🔴 | **Allerta attacchi attivi** — indica gli IP che tentano ancora dopo il ban |

---

### 📸 Screenshot

**Dashboard principale:**

```
==============================================================================
          FAIL2BAN MANAGER — SSH Protection                            [IT]
==============================================================================
  10/05/2026 09:15:42
==============================================================================

  Tentativi falliti totali : 1482
  IP bannati attualmente   : 3
  IP bannati (storico)     : 214
  Ban time (default)       : 7g
  Ordinamento              : per data ban (recenti prima)

  #     IP               CC  Ultimo ban           Residuo    Tot  Tentativi
  ──────────────────────────────────────────────────────────────────────────
  [1 ]  203.0.113.45     CN  2026-05-09 13:10:01  6g 22h      47  ████████░░  🔴 +3
  [2 ]  198.51.100.12    RU  2026-05-08 09:44:17  5g 19h      23  ████░░░░░░
  [3 ]  192.0.2.77       US  2026-05-07 21:05:55  4g 6h       11  ██░░░░░░░░

  [r] Aggiorna          [t] Statistiche avanzate
  [u] Sbanna un IP      [g] Lingua / Language  →  EN
  [b] Gestisci ban time [q] Esci
  [s] Cambia ordinamento
  [l] Ultimi eventi dal log
```

**Schermata statistiche avanzate `[t]`:**

```
==============================================================================
          FAIL2BAN MANAGER — SSH Protection                            [IT]
==============================================================================
  10/05/2026 09:16:03
==============================================================================

  ── STATISTICHE AVANZATE ──

  IP bannati (storico): 214

  TOP 5 IP PIÙ AGGRESSIVI DI SEMPRE  (log corrente)
  ──────────────────────────────────────────────────────────────────
  203.0.113.45        CN  ████████████████████   847  China
  198.51.100.12       RU  ████████████░░░░░░░░   512  Russia
  45.142.212.100      DE  ████████░░░░░░░░░░░░   341  Germany
  91.240.118.9        UA  █████░░░░░░░░░░░░░░░   198  Ukraine
  185.220.101.55      NL  ███░░░░░░░░░░░░░░░░░   104  Netherlands

  DISTRIBUZIONE GEOGRAFICA — BANNATI ATTUALI
  ──────────────────────────────────────────────────────────────────
  CN    China                           ████████████████████   47  (57%)
  RU    Russia                          ██████████░░░░░░░░░░   27  (33%)
  US    United States                   ████░░░░░░░░░░░░░░░░    8  (10%)
```

---

### ⚙️ Prerequisiti

- **Linux** — Debian, Ubuntu, CentOS, Rocky, Alma o qualsiasi distro con systemd
- **Python 3.6+** — preinstallato su quasi tutte le distro moderne
- **fail2ban** — installato e attivo con la jail `sshd`
- **geoip-bin** *(opzionale ma raccomandato)* — per la geolocalizzazione degli IP

> ⚠️ **Senza `geoip-bin`** il programma funziona normalmente, ma la colonna `CC` mostrerà `??` e le funzioni geografiche saranno disabilitate.

---

### 📦 Installazione fail2ban

#### Debian / Ubuntu
```bash
sudo apt update && sudo apt install fail2ban -y
```

#### CentOS / Rocky Linux / AlmaLinux
```bash
sudo dnf install epel-release -y && sudo dnf install fail2ban -y
```

#### Arch Linux
```bash
sudo pacman -S fail2ban
```

#### Avvia il servizio
```bash
sudo systemctl enable --now fail2ban
sudo systemctl status fail2ban
```

---

### 🌍 Installazione geoip-bin (geolocalizzazione)

```bash
# Debian / Ubuntu
sudo apt install geoip-bin -y

# CentOS / Rocky / Alma
sudo dnf install GeoIP -y

# Arch
sudo pacman -S geoip
```

Verifica che funzioni:
```bash
geoiplookup 8.8.8.8
# GeoIP Country Edition: US, United States
```

> 💡 Se non installi `geoip-bin`, f2b-manager continua a funzionare perfettamente — si limiterà a mostrare `??` nella colonna paese.

---

### 🔧 Configurare fail2ban per SSH

Crea il file di configurazione personalizzato (non toccare mai i file `.conf` originali):

```bash
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
# Ignora sempre il tuo IP personale
ignoreip = 127.0.0.1/8 ::1

# Finestra di osservazione (secondi)
findtime  = 600

# Tentativi massimi prima del ban
maxretry  = 5

# Durata ban in secondi (-1 = permanente)
bantime   = 86400

[sshd]
enabled  = true
port     = ssh
logpath  = %(sshd_log)s
backend  = %(sshd_backend)s
```

```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd   # verifica
```

---

### 🚀 Installazione f2b-manager

```bash
git clone https://github.com/Pier-86/f2b-manager.git
cd f2b-manager
chmod +x f2b-manager.py   # opzionale
```

Nessuna dipendenza esterna — usa solo la libreria standard Python.

---

### ▶️ Utilizzo

```bash
python3 f2b-manager.py
```

Lo script rileva automaticamente se non è root e si ri-esegue con `sudo`.

---

### ⌨️ Comandi

| Tasto | Azione |
|:-----:|--------|
| `r` | Aggiorna la dashboard |
| `u` | Sbanna un IP (per numero o indirizzo completo) |
| `b` | Menu gestione ban time (globale o per singolo IP) |
| `s` | Cambia ordinamento (IP / data / tentativi) |
| `l` | Ultimi 20 eventi dal log (Ban / Unban / Found) |
| `t` | Statistiche avanzate — Top 5 e mappa geografica |
| `g` | Cambia lingua  IT ↔ EN |
| `q` | Esci |

---

### 🔬 Note tecniche

- Il **tempo residuo** è letto dal database SQLite (`/var/lib/fail2ban/fail2ban.sqlite3`) — preciso al secondo, non stimato.
- Il cambio ban time per singolo IP: `unban → nuovo bantime → re-ban → ripristino bantime originale`.
- L'indicatore **🔴 +N** segnala tentativi `Found` registrati *dopo* l'ultimo ban — l'attacco è ancora in corso.
- Il **grafico a barre** è relativo agli IP attualmente bannati: la barra più piena = IP più aggressivo del gruppo.
- Il **contatore storico** e il **Top 5** usano il log corrente (`/var/log/fail2ban.log`) — i log ruotati non vengono letti.
- La **geolocalizzazione** è in cache per tutta la sessione: il lookup avviene una sola volta per IP.

---

### 📄 Licenza

**MIT** — libero di usare, modificare e distribuire.

---
---

## 🇬🇧 English

### What is f2b-manager?

`f2b-manager` is a **TUI (Terminal User Interface)** tool written in pure Python that lets you manage **fail2ban** in a simple, visual, and immediate way — directly from your server's terminal.

No external dependencies. No framework. Launch it and you have everything under control.

---

### ✨ Features

| | Feature |
|---|---|
| 🌍 | **Geolocation** — country of origin for each IP in the table (`CC`) |
| 📊 | **ASCII bar chart** — relative aggressiveness of each IP, visual and immediate |
| 📈 | **Historical counter** — total distinct IPs ever banned (SQLite) |
| 🏆 | **All-time Top 5** — most aggressive IPs ever, with bars and country |
| 🗺️ | **Geo map** — attack distribution by country with percentages |
| ⏱️ | **Precise remaining time** — read from fail2ban's SQLite database, to the second |
| 🔧 | **Ban time management** — global or per-IP (unban + re-ban) |
| 🔢 | **Ready presets** — 1d, 5d, 7d, 10d, 15d, 30d, permanent · or custom input |
| ↕️ | **Flexible sorting** — IP, ban date, number of attempts |
| 🌐 | **Bilingual IT/EN** — switch language on the fly with `[g]` |
| 🔐 | **Auto root** — re-runs itself with `sudo` automatically |
| 🔴 | **Active attack alert** — flags IPs still attempting after the ban |

---

### 📸 Screenshot

**Main dashboard:**

```
==============================================================================
          FAIL2BAN MANAGER — SSH Protection                            [EN]
==============================================================================
  10/05/2026 09:15:42
==============================================================================

  Total failed attempts    : 1482
  Currently banned IPs     : 3
  IPs banned (all time)    : 214
  Ban time (default)       : 7d
  Sort order               : by ban date (most recent first)

  #     IP               CC  Last ban             Remaining  Tot  Attempts
  ──────────────────────────────────────────────────────────────────────────
  [1 ]  203.0.113.45     CN  2026-05-09 13:10:01  6d 22h      47  ████████░░  🔴 +3
  [2 ]  198.51.100.12    RU  2026-05-08 09:44:17  5d 19h      23  ████░░░░░░
  [3 ]  192.0.2.77       US  2026-05-07 21:05:55  4d 6h       11  ██░░░░░░░░

  [r] Refresh             [t] Advanced statistics
  [u] Unban an IP         [g] Lingua / Language  →  IT
  [b] Manage ban time     [q] Quit
  [s] Change sort order
  [l] Last log events
```

**Advanced statistics screen `[t]`:**

```
==============================================================================
          FAIL2BAN MANAGER — SSH Protection                            [EN]
==============================================================================
  10/05/2026 09:16:03
==============================================================================

  ── ADVANCED STATISTICS ──

  IPs banned (all time): 214

  TOP 5 MOST AGGRESSIVE IPs OF ALL TIME  (current log)
  ──────────────────────────────────────────────────────────────────
  203.0.113.45        CN  ████████████████████   847  China
  198.51.100.12       RU  ████████████░░░░░░░░   512  Russia
  45.142.212.100      DE  ████████░░░░░░░░░░░░   341  Germany
  91.240.118.9        UA  █████░░░░░░░░░░░░░░░   198  Ukraine
  185.220.101.55      NL  ███░░░░░░░░░░░░░░░░░   104  Netherlands

  GEO BREAKDOWN — CURRENTLY BANNED IPs
  ──────────────────────────────────────────────────────────────────
  CN    China                           ████████████████████   47  (57%)
  RU    Russia                          ██████████░░░░░░░░░░   27  (33%)
  US    United States                   ████░░░░░░░░░░░░░░░░    8  (10%)
```

---

### ⚙️ Prerequisites

- **Linux** — Debian, Ubuntu, CentOS, Rocky, Alma or any systemd-based distro
- **Python 3.6+** — pre-installed on virtually all modern distros
- **fail2ban** — installed and running with the `sshd` jail active
- **geoip-bin** *(optional but recommended)* — for IP geolocation

> ⚠️ **Without `geoip-bin`** the program works normally, but the `CC` column will show `??` and geo features will be disabled.

---

### 📦 Install fail2ban

#### Debian / Ubuntu
```bash
sudo apt update && sudo apt install fail2ban -y
```

#### CentOS / Rocky Linux / AlmaLinux
```bash
sudo dnf install epel-release -y && sudo dnf install fail2ban -y
```

#### Arch Linux
```bash
sudo pacman -S fail2ban
```

#### Start the service
```bash
sudo systemctl enable --now fail2ban
sudo systemctl status fail2ban
```

---

### 🌍 Install geoip-bin (geolocation)

```bash
# Debian / Ubuntu
sudo apt install geoip-bin -y

# CentOS / Rocky / Alma
sudo dnf install GeoIP -y

# Arch
sudo pacman -S geoip
```

Verify it works:
```bash
geoiplookup 8.8.8.8
# GeoIP Country Edition: US, United States
```

> 💡 If you skip `geoip-bin`, f2b-manager keeps working perfectly — it will simply show `??` in the country column.

---

### 🔧 Configure fail2ban for SSH

Create a custom config file (never edit the original `.conf` files):

```bash
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
# Always ignore your own IP
ignoreip = 127.0.0.1/8 ::1

# Observation window (seconds)
findtime  = 600

# Max attempts before ban
maxretry  = 5

# Ban duration in seconds (-1 = permanent)
bantime   = 86400

[sshd]
enabled  = true
port     = ssh
logpath  = %(sshd_log)s
backend  = %(sshd_backend)s
```

```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd   # verify
```

---

### 🚀 Install f2b-manager

```bash
git clone https://github.com/Pier-86/f2b-manager.git
cd f2b-manager
chmod +x f2b-manager.py   # optional
```

No external dependencies — pure Python standard library only.

---

### ▶️ Usage

```bash
python3 f2b-manager.py
```

The script automatically detects if it's not running as root and re-launches itself with `sudo`.

---

### ⌨️ Keyboard controls

| Key | Action |
|:---:|--------|
| `r` | Refresh the dashboard |
| `u` | Unban an IP (by number or full address) |
| `b` | Ban time menu (global or per-IP) |
| `s` | Change sort order (IP / date / attempts) |
| `l` | Last 20 log events (Ban / Unban / Found) |
| `t` | Advanced statistics — Top 5 and geo map |
| `g` | Switch language  IT ↔ EN |
| `q` | Quit |

---

### 🔬 Technical notes

- **Remaining time** is read from the SQLite database (`/var/lib/fail2ban/fail2ban.sqlite3`) — accurate to the second, not estimated.
- Per-IP ban time change: `unban → set new bantime → re-ban → restore original bantime`.
- The **🔴 +N** indicator flags `Found` events recorded *after* the last ban — the attack is still ongoing.
- The **bar chart** is relative to currently banned IPs: the fullest bar = most aggressive IP in the current group.
- The **historical counter** and **Top 5** use the current log (`/var/log/fail2ban.log`) — rotated logs are not read.
- **Geolocation** is cached for the entire session: lookup runs only once per IP.

---

### 📄 License

**MIT** — free to use, modify, and distribute.
