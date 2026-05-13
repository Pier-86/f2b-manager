<div align="center">

# 🛡️ f2b-manager

### Fail2ban Manager — TUI + Web Dashboard + Docker

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Synology-FCC624?logo=linux&logoColor=black)](https://kernel.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)
[![Language](https://img.shields.io/badge/Language-IT%20%7C%20EN-8b5cf6)]()
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)]()

<br>

*Gestisci fail2ban dal terminale o dal browser — con supporto multi-jail e Synology.*
*Manage fail2ban from terminal or browser — with multi-jail and Synology support.*

<br>

**🇮🇹 [Italiano](#-italiano) · 🇬🇧 [English](#-english)**

</div>

---

## 🇮🇹 Italiano

### Cos'è f2b-manager?

`f2b-manager` è uno strumento completo per gestire **fail2ban** con due interfacce:

- **TUI** (Terminal User Interface) — dashboard interattiva da terminale, zero dipendenze
- **Web App** — dashboard moderna via browser con API REST, deployabile con Docker

Supporta **jails multipli** (`sshd`, `synology-dsm`, `nginx-http-auth`, `postfix`, ecc.) e funziona su **Linux** e **Synology DSM**.

---

### ✨ Funzionalità

| | Funzione |
|---|---|
| 🌍 | **Geolocalizzazione** — paese di origine di ogni IP |
| 📊 | **Grafico a barre ASCII** — aggressività relativa di ogni IP |
| 📈 | **Contatore storico** — IP distinti bannati dall'inizio (SQLite) |
| 🏆 | **Top 5 di sempre** — IP più aggressivi con barre e paese |
| 🗺️ | **Mappa geografica** — distribuzione attacchi per paese con percentuali |
| ⏱️ | **Tempo residuo preciso** — dal database SQLite, al secondo |
| 🔧 | **Gestione ban time** — modifica globale o per singolo IP |
| 🔢 | **Preset pronti** — 1g, 5g, 7g, 10g, 15g, 30g, permanente |
| ↕️ | **Ordinamento flessibile** — IP, data ban, numero tentativi |
| 🌐 | **Multilingua IT/EN** — cambia lingua al volo con `[g]` |
| 🔐 | **Auto root** (TUI) + **API Key auth** (Web) |
| 🔴 | **Allerta attacchi attivi** — IP che tentano ancora dopo il ban |
| 🔄 | **Multi-jail** — seleziona jail da gestire (SSH, Synology, Nginx, ...) |
| 🖥️ | **Web UI** — dashboard moderna con Tailwind CSS e auto-refresh 30s |
| 🐳 | **Docker** — container non-root con mount dei volumi host |
| 🎨 | **Tema chiaro/scuro** — toggle nella web UI |
| 🔒 | **Rate limiting** — protezione API (60 req/min per IP) |

---

### 📸 Screenshot

**Dashboard principale (TUI):**
```
==============================================================================
          FAIL2BAN MANAGER — sshd                               [sshd]   [IT]
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

  [r] Aggiorna              [j] Cambia jail  (sshd)
  [u] Sbanna un IP          [t] Statistiche avanzate
  [b] Gestisci ban time     [g] Lingua / Language  →  EN
  [s] Cambia ordinamento    [q] Esci
  [l] Ultimi eventi dal log
```

**Web Dashboard:**
La web UI offre le stesse funzionalità con un'interfaccia moderna, selettore jail, filtro per paese, ordinamento cliccabile sulle colonne, tema chiaro/scuro e auto-refresh ogni 30 secondi.

---

### ⚙️ Prerequisiti

- **Linux** o **Synology DSM** (con fail2ban installato)
- **Python 3.11+** (per la TUI)
- **fail2ban** — installato e attivo
- **geoip-bin** *(opzionale)* — per la geolocalizzazione IP
- **Docker** *(opzionale)* — per la web app

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

#### Synology DSM
fail2ban è disponibile tramite il **Centro Pacchetti Synology** o via **Entware**:
```bash
# Via Entware (dopo aver installato entware)
opkg install fail2ban
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

---

### 🔧 Configurare fail2ban

Crea `/etc/fail2ban/jail.local`:

```ini
[DEFAULT]
ignoreip = 127.0.0.1/8 ::1
findtime  = 600
maxretry  = 5
bantime   = 86400

[sshd]
enabled  = true
port     = ssh
logpath  = %(sshd_log)s
backend  = %(sshd_backend)s

# Synology DSM (se applicabile)
[synology-dsm]
enabled  = true
logpath  = /var/log/synolog/synolog.log
```

```bash
sudo systemctl restart fail2ban
```

---

### 🚀 Utilizzo TUI

```bash
git clone https://github.com/Pier-86/f2b-manager.git
cd f2b-manager
python3 f2b-manager.py
```

Lo script si auto-eleva a root con `sudo` e supporta le variabili d'ambiente:
- `F2B_JAIL=jail_name` — jail iniziale
- `F2B_LANG=it|en` — lingua predefinita

#### ⌨️ Comandi TUI

| Tasto | Azione |
|:-----:|--------|
| `r` | Aggiorna la dashboard |
| `j` | Cambia jail (se multipli configurati) |
| `u` | Sbanna un IP |
| `b` | Menu gestione ban time |
| `s` | Cambia ordinamento |
| `l` | Ultimi 20 eventi dal log |
| `t` | Statistiche avanzate |
| `g` | Cambia lingua IT ↔ EN |
| `q` | Esci |

---

### 🐳 Deploy Web App (Docker)

#### Con Docker Compose (consigliato)

Crea un file `.env`:
```bash
F2B_API_KEY=la-tua-chiave-segreta
```

Poi:
```bash
docker-compose up -d
```

#### Con Docker direttamente
```bash
docker run -d --name f2b-manager-web \
  -p 8080:8080 \
  -e F2B_API_KEY=la-tua-chiave-segreta \
  -e F2B_JAILS=sshd,synology-dsm,nginx-http-auth \
  -v /var/run/fail2ban:/var/run/fail2ban \
  -v /var/lib/fail2ban:/var/lib/fail2ban:ro \
  -v /var/log/fail2ban.log:/var/log/fail2ban.log:ro \
  -v /var/log/auth.log:/var/log/auth.log:ro \
  pier86/f2b-manager:latest
```

#### Variabili d'ambiente

| Variabile | Default | Descrizione |
|---|---|---|
| `F2B_JAILS` | `sshd` | Lista jails separata da virgola |
| `F2B_JAIL` | Primo da `F2B_JAILS` | Jail attiva all'avvio |
| `F2B_API_KEY` | *(vuoto)* | Se impostata, richiede auth su tutte le API |
| `F2B_API_RATE_LIMIT` | `60` | Max richieste per finestra |
| `F2B_API_RATE_WINDOW` | `60` | Finestra in secondi |
| `F2B_DB` | auto-detect | Path database SQLite |
| `F2B_LOG` | auto-detect | Path log fail2ban |
| `F2B_GEOIP_BIN` | `geoiplookup` | Binary per geolocalizzazione |

#### Volumi necessari

| Volume | Descrizione |
|---|---|
| `/var/run/fail2ban` | Socket Unix (lettura/scrittura) |
| `/var/lib/fail2ban` | Database SQLite (sola lettura) |
| `/var/log/fail2ban.log` | Log fail2ban (sola lettura) |
| `/var/log/auth.log` | Log auth (opzionale, per SSH) |

---

### 🛡️ Sicurezza

Le seguenti protezioni sono implementate nel codice:

| Area | Protezione |
|---|---|
| **Shell injection** | Ogni IP è validato con `ipaddress.ip_address()`; ogni jail name è controllato con regex `[a-zA-Z0-9_-]{1,64}` prima di qualsiasi comando shell. I path dei file passati a shell sono quotati con `shlex.quote()`. |
| **XSS (Web UI)** | Tutti i valori provenienti dall'API (IP, paese, jail name) sono escapati con `escHtml()` prima di essere inseriti nel DOM. Il bottone Unban usa `data-ip` invece di `onclick` con stringa interpolata. |
| **API Key auth** | Confronto a tempo costante (`secrets.compare_digest`) — immune a timing attack. |
| **Rate limiting** | 60 req/min per IP (configurabile); i bucket scaduti vengono eliminati ad ogni richiesta per evitare crescita illimitata in memoria. |
| **Geo cache** | Limitata a 1024 entry con evizione FIFO per contenere l'uso di RAM. |
| **SQLite** | Le connessioni sono chiuse in blocco `try/finally` anche in caso di eccezione. |
| **Docker** | Container non-root (utente `f2b`, uid 1001); solo i volumi strettamente necessari. |

> **Raccomandazione**: imposta sempre `F2B_API_KEY` quando esponi la web app su rete pubblica o LAN non fidata.

---

### 🔬 Note tecniche

- Il **modulo condiviso** `f2b_core.py` contiene tutta la logica (jail operations, geo, i18n, parsing), usata sia dalla TUI che dalla web app.
- Il **tempo residuo** è letto dal database SQLite — preciso al secondo, non stimato.
- Il cambio ban time per singolo IP: `unban → nuovo bantime → re-ban → ripristino`.
- L'indicatore **🔴 +N** segnala tentativi `Found` dopo l'ultimo ban — attacco in corso.
- Il **parsing log è incrementale**: ad ogni refresh vengono lette solo le nuove righe.
- Rilevamento automatico **Synology**: se rileva `/etc/synoinfo.conf`, cerca i percorsi alternativi.
- La **geolocalizzazione** è in cache in memoria (max 1024 entry, evizione FIFO).
- I test sono in `tests/`: `python3 -m pytest tests/ -v`.

---

### 📄 Licenza

**MIT** — libero di usare, modificare e distribuire.

---

---

## 🇬🇧 English

### What is f2b-manager?

`f2b-manager` is a complete **fail2ban management** tool with two interfaces:

- **TUI** (Terminal User Interface) — interactive terminal dashboard, zero dependencies
- **Web App** — modern browser dashboard with REST API, Docker-ready

Supports **multiple jails** (`sshd`, `synology-dsm`, `nginx-http-auth`, `postfix`, etc.) and runs on **Linux** and **Synology DSM**.

---

### ✨ Features

| | Feature |
|---|---|
| 🌍 | **Geolocation** — country of origin for each IP |
| 📊 | **ASCII bar chart** — relative aggressiveness of each IP |
| 📈 | **Historical counter** — total distinct IPs ever banned |
| 🏆 | **All-time Top 5** — most aggressive IPs with bars and country |
| 🗺️ | **Geo map** — attack distribution by country with percentages |
| ⏱️ | **Precise remaining time** — from fail2ban's SQLite DB |
| 🔧 | **Ban time management** — global or per-IP (unban + re-ban) |
| 🔢 | **Ready presets** — 1d, 5d, 7d, 10d, 15d, 30d, permanent |
| ↕️ | **Flexible sorting** — IP, ban date, number of attempts |
| 🌐 | **Bilingual IT/EN** — switch language on the fly |
| 🔐 | **Auto root** (TUI) + **API Key auth** (Web) |
| 🔴 | **Active attack alert** — flags IPs still attempting after ban |
| 🔄 | **Multi-jail** — select jail to manage (SSH, Synology, Nginx...) |
| 🖥️ | **Web UI** — dark modern dashboard with Tailwind CSS, 30s auto-refresh |
| 🐳 | **Docker** — non-root container with host volume mounts |
| 🎨 | **Light/Dark theme** — toggle in web UI |
| 🔒 | **Rate limiting** — API protection (60 req/min per IP) |

---

### 🚀 Quick start

#### TUI (host)
```bash
git clone https://github.com/Pier-86/f2b-manager.git
cd f2b-manager
python3 f2b-manager.py
```

#### Web (Docker)
```bash
docker run -d --name f2b-manager-web \
  -p 8080:8080 \
  -e F2B_API_KEY=your-secret-key \
  -v /var/run/fail2ban:/var/run/fail2ban \
  -v /var/lib/fail2ban:/var/lib/fail2ban:ro \
  -v /var/log/fail2ban.log:/var/log/fail2ban.log:ro \
  pier86/f2b-manager:latest
```

Then open http://your-server:8080.

---

#### Keyboard controls (TUI)

| Key | Action |
|:---:|--------|
| `r` | Refresh dashboard |
| `j` | Switch jail (if multiple configured) |
| `u` | Unban an IP |
| `b` | Ban time menu |
| `s` | Change sort order |
| `l` | Last 20 log events |
| `t` | Advanced statistics |
| `g` | Switch language IT ↔ EN |
| `q` | Quit |

---

### 🔧 Configuration via environment variables

| Variable | Default | Description |
|---|---|---|
| `F2B_JAILS` | `sshd` | Comma-separated list of jails |
| `F2B_JAIL` | First from `F2B_JAILS` | Active jail at startup |
| `F2B_API_KEY` | *(empty)* | If set, requires auth on all API endpoints |
| `F2B_API_RATE_LIMIT` | `60` | Max requests per window |
| `F2B_API_RATE_WINDOW` | `60` | Window in seconds |
| `F2B_DB` | auto-detect | SQLite database path |
| `F2B_LOG` | auto-detect | fail2ban log path |
| `F2B_GEOIP_BIN` | `geoiplookup` | Geolocation binary |

---

### 🛡️ Security

The following protections are implemented in the codebase:

| Area | Protection |
|---|---|
| **Shell injection** | Every IP is validated with `ipaddress.ip_address()`; every jail name is checked against `[a-zA-Z0-9_-]{1,64}` before any shell command. File paths passed to the shell are quoted with `shlex.quote()`. |
| **XSS (Web UI)** | All API-derived values (IP, country, jail name) are escaped with `escHtml()` before DOM insertion. The Unban button uses a `data-ip` attribute instead of an interpolated `onclick` string. |
| **API Key auth** | Constant-time comparison via `secrets.compare_digest` — immune to timing attacks. |
| **Rate limiting** | 60 req/min per IP (configurable); expired buckets are removed on each request to prevent unbounded memory growth. |
| **Geo cache** | Capped at 1024 entries with FIFO eviction to bound RAM usage. |
| **SQLite** | Connections are closed in `try/finally` blocks even when an exception occurs. |
| **Docker** | Non-root container (user `f2b`, uid 1001); only strictly necessary volume mounts. |

> **Recommendation**: always set `F2B_API_KEY` when exposing the web app on a public or untrusted LAN.

---

### 🔬 Technical notes

- **Shared module** `f2b_core.py` contains all common logic, used by both TUI and web app.
- **Remaining time** is read from fail2ban's SQLite DB — accurate to the second.
- Per-IP ban time change: `unban → set bantime → re-ban → restore original`.
- **🔴 +N** indicator flags `Found` events after the last ban — attack still ongoing.
- **Incremental log parsing**: only new lines are read on each refresh.
- **Synology auto-detection**: if `/etc/synoinfo.conf` exists, alternative paths are probed.
- **Geolocation** is cached in memory (max 1024 entries, FIFO eviction).
- Tests in `tests/`: `python3 -m pytest tests/ -v`.

---

### 📄 License

**MIT** — free to use, modify, and distribute.
