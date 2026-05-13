<div align="center">

# 🛡️ f2b-manager

**Fail2ban Manager — TUI · Web Dashboard · REST API · Docker**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white&style=for-the-badge)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white&style=for-the-badge)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white&style=for-the-badge)](https://hub.docker.com/r/pier86/f2b-manager)
[![Tests](https://img.shields.io/badge/Tests-65%20passed-22c55e?logo=pytest&logoColor=white&style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-f59e0b?style=for-the-badge)](LICENSE)

<br/>

*Gestisci fail2ban dal terminale o dal browser — multi-jail, geo, Docker-ready.*
<br/>
*Manage fail2ban from terminal or browser — multi-jail, geolocation, Docker-ready.*

<br/>

**[🇮🇹 Italiano](#-italiano) · [🇬🇧 English](#-english)**

</div>

---

## 🇮🇹 Italiano

<details open>
<summary><b>📑 Indice</b></summary>

- [Cos'è](#cosè-f2b-manager)
- [Funzionalità](#-funzionalità)
- [Screenshot](#-screenshot)
- [Prerequisiti](#️-prerequisiti)
- [Installazione fail2ban](#-installazione-fail2ban)
- [Geolocalizzazione](#-geolocalizzazione-opzionale)
- [Configurazione](#-configurare-fail2ban)
- [TUI — utilizzo](#️-utilizzo-tui)
- [Web App — Docker Compose](#-docker-compose)
- [Web App — Coolify](#-coolify)
- [Web App — Docker diretto](#-docker-diretto)
- [Variabili d'ambiente](#️-variabili-dambiente)
- [Sicurezza](#️-sicurezza)
- [Note tecniche](#-note-tecniche)

</details>

---

### Cos'è f2b-manager?

`f2b-manager` è uno strumento completo per gestire **fail2ban** con due interfacce:

<table>
<tr>
<td align="center" width="50%">

### 🖥️ TUI
Dashboard interattiva da terminale.<br/>
Zero dipendenze extra, gira su qualsiasi Linux.

</td>
<td align="center" width="50%">

### 🌐 Web App
Dashboard moderna via browser con REST API.<br/>
Deployabile con Docker, Coolify o bare metal.

</td>
</tr>
</table>

Supporta **jail multipli** (`sshd`, `synology-dsm`, `nginx-http-auth`, `postfix`, ...) e funziona su **Linux** e **Synology DSM**.

---

### ✨ Funzionalità

<table>
<tr>
<th>📡 Monitoraggio</th>
<th>🔧 Gestione</th>
<th>🚀 Deploy</th>
</tr>
<tr>
<td>

🌍 Geolocalizzazione IP<br/>
📊 Barre ASCII aggressività<br/>
📈 Contatore storico SQLite<br/>
🏆 Top 5 IP più aggressivi<br/>
🗺️ Distribuzione geografica<br/>
⏱️ Tempo residuo al secondo<br/>
🔴 Alert attacchi attivi

</td>
<td>

🔒 Ban/unban IP<br/>
🔧 Ban time globale e per IP<br/>
🔢 Preset: 1g · 5g · 7g · 10g · 15g · 30g · ∞<br/>
↕️ Ordinamento per IP / data / tentativi<br/>
🔄 Selezione multi-jail<br/>
🌐 Interfaccia IT / EN<br/>
📋 Ultimi 20 eventi dal log

</td>
<td>

🐳 Container non-root<br/>
🧊 Coolify (una-click)<br/>
🔐 API Key auth<br/>
🛡️ Input validation & XSS protection<br/>
⏱️ Rate limiting 60 req/min<br/>
🎨 Tema chiaro / scuro<br/>
♻️ Auto-refresh 30s

</td>
</tr>
</table>

---

### 📸 Screenshot

**TUI — Dashboard principale:**

```
==============================================================================
          FAIL2BAN MANAGER — sshd                               [sshd]   [IT]
==============================================================================
  13/05/2026 09:15:42
==============================================================================

  Tentativi falliti totali : 1482
  IP bannati attualmente   : 3
  IP bannati (storico)     : 214
  Ban time (default)       : 7g
  Ordinamento              : per data ban (recenti prima)

  #     IP               CC  Ultimo ban           Residuo    Tot  Tentativi
  ──────────────────────────────────────────────────────────────────────────
  [1 ]  203.0.113.45     CN  2026-05-12 13:10:01  6g 22h      47  ████████░░  🔴 +3
  [2 ]  198.51.100.12    RU  2026-05-11 09:44:17  5g 19h      23  ████░░░░░░
  [3 ]  192.0.2.77       US  2026-05-10 21:05:55  4g  6h      11  ██░░░░░░░░

  [r] Aggiorna              [j] Cambia jail  (sshd)
  [u] Sbanna un IP          [t] Statistiche avanzate
  [b] Gestisci ban time     [g] Lingua / Language  →  EN
  [s] Cambia ordinamento    [q] Esci
  [l] Ultimi eventi dal log
```

**Web Dashboard:** selettore jail, filtro paese, ordinamento cliccabile su ogni colonna, tema chiaro/scuro e auto-refresh ogni 30 secondi.

---

### ⚙️ Prerequisiti

| Componente | Richiesto | Note |
|---|:---:|---|
| Linux o Synology DSM | ✅ | fail2ban deve essere installato e attivo |
| Python 3.11+ | Solo TUI | Non serve per la web app via Docker |
| Docker | Solo Web | Opzionale — si può usare anche bare metal |
| geoip-bin | ❌ | Opzionale — abilita la geolocalizzazione IP |

---

### 📦 Installazione fail2ban

<details>
<summary><b>🟠 Debian / Ubuntu</b></summary>

```bash
sudo apt update && sudo apt install fail2ban -y
sudo systemctl enable --now fail2ban
```

</details>

<details>
<summary><b>🔵 CentOS / Rocky Linux / AlmaLinux</b></summary>

```bash
sudo dnf install epel-release -y
sudo dnf install fail2ban -y
sudo systemctl enable --now fail2ban
```

</details>

<details>
<summary><b>🟣 Arch Linux</b></summary>

```bash
sudo pacman -S fail2ban
sudo systemctl enable --now fail2ban
```

</details>

<details>
<summary><b>🟢 Synology DSM</b></summary>

fail2ban è disponibile via **Centro Pacchetti Synology** oppure via **Entware**:

```bash
opkg install fail2ban
```

</details>

---

### 🌍 Geolocalizzazione *(opzionale)*

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
ignoreip  = 127.0.0.1/8 ::1
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

### 🖥️ Utilizzo TUI

```bash
git clone https://github.com/Pier-86/f2b-manager.git
cd f2b-manager
python3 f2b-manager.py   # si auto-eleva con sudo
```

**Variabili d'ambiente opzionali:**

```bash
F2B_JAIL=sshd    # jail iniziale (default: sshd)
F2B_LANG=en      # lingua: it (default) | en
```

**Comandi tastiera:**

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

### 🐳 Deploy Web App

---

#### 🐋 Docker Compose

```bash
git clone https://github.com/Pier-86/f2b-manager.git
cd f2b-manager

# Crea il file di configurazione
echo "F2B_API_KEY=la-tua-chiave-segreta" > .env

# Avvia
docker-compose up -d
```

Apri `http://localhost:8080`.

---

#### 🧊 Coolify

> **⚠️ Requisito fondamentale**: Coolify deve girare sullo **stesso server** dove è installato fail2ban. Il container accede al socket Unix dell'host — non è possibile puntare a un server remoto.

**Passo 1 — Nuovo servizio**

In Coolify: **New Resource → Docker Compose (Empty)**

**Passo 2 — Incolla il Compose**

```yaml
services:
  f2b-web:
    image: pier86/f2b-manager:latest
    restart: unless-stopped
    environment:
      - F2B_JAILS=sshd
      - F2B_JAIL=sshd
      - F2B_API_KEY=${F2B_API_KEY}
      - F2B_API_RATE_LIMIT=60
      - F2B_API_RATE_WINDOW=60
    volumes:
      - /var/run/fail2ban:/var/run/fail2ban
      - /var/lib/fail2ban:/var/lib/fail2ban:ro
      - /var/log/fail2ban.log:/var/log/fail2ban.log:ro
      - /var/log/auth.log:/var/log/auth.log:ro
    ports:
      - "8080:8080"
```

**Passo 3 — Environment Variables**

Nel tab **Environment Variables** di Coolify aggiungi:

```
F2B_API_KEY=una-chiave-lunga-e-casuale
```

**Passo 4 — Dominio e HTTPS**

Nel tab **Domains** aggiungi il tuo sottodominio (es. `f2b.tuodominio.com`).
Coolify configura **Traefik + Let's Encrypt** automaticamente.

**Passo 5 — Deploy**

Clicca **Deploy** e attendi. L'immagine viene scaricata da Docker Hub, i volumi vengono montati e il servizio parte.

```
Internet → Traefik (Coolify) → HTTPS → f2b-manager:8080
                                              ↓
                              /var/run/fail2ban/fail2ban.sock  (host, rw)
                              /var/lib/fail2ban/fail2ban.sqlite3  (host, ro)
                              /var/log/fail2ban.log  (host, ro)
```

**Problema permessi socket?**

Il container gira come utente non-root (uid 1001). Il socket di fail2ban sull'host appartiene tipicamente a `root:root 660`, quindi il container non può accedervi. Soluzione: aggiungi un **override systemd** sull'host che allarga i permessi ad ogni avvio di fail2ban:

```bash
sudo mkdir -p /etc/systemd/system/fail2ban.service.d/

sudo tee /etc/systemd/system/fail2ban.service.d/socket-perms.conf << 'EOF'
[Service]
ExecStartPost=/bin/chmod 666 /var/run/fail2ban/fail2ban.sock
EOF

sudo systemctl daemon-reload && sudo systemctl restart fail2ban
```

> Questa configurazione è permanente e sopravvive ai riavvii.

---

#### 🐟 Docker diretto

```bash
docker run -d \
  --name f2b-manager-web \
  --restart unless-stopped \
  -p 8080:8080 \
  -e F2B_API_KEY=la-tua-chiave-segreta \
  -e F2B_JAILS=sshd,nginx-http-auth,postfix \
  -v /var/run/fail2ban:/var/run/fail2ban \
  -v /var/lib/fail2ban:/var/lib/fail2ban:ro \
  -v /var/log/fail2ban.log:/var/log/fail2ban.log:ro \
  -v /var/log/auth.log:/var/log/auth.log:ro \
  pier86/f2b-manager:latest
```

---

### ⚙️ Variabili d'ambiente

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| `F2B_JAILS` | `sshd` | Lista jail separata da virgola |
| `F2B_JAIL` | Primo da `F2B_JAILS` | Jail attiva all'avvio |
| `F2B_API_KEY` | *(vuoto)* | Se impostata, richiede auth su tutte le API |
| `F2B_API_RATE_LIMIT` | `60` | Max richieste per finestra |
| `F2B_API_RATE_WINDOW` | `60` | Finestra in secondi |
| `F2B_DB` | auto-detect | Path database SQLite di fail2ban |
| `F2B_LOG` | auto-detect | Path log fail2ban |
| `F2B_GEOIP_BIN` | `geoiplookup` | Binary per la geolocalizzazione |

**Volumi richiesti:**

| Volume host | Mount container | Permessi | Scopo |
|-------------|----------------|:--------:|-------|
| `/var/run/fail2ban` | `/var/run/fail2ban` | `rw` | Socket Unix — comandi ban/unban |
| `/var/lib/fail2ban` | `/var/lib/fail2ban` | `ro` | Database SQLite — tempo residuo |
| `/var/log/fail2ban.log` | `/var/log/fail2ban.log` | `ro` | Log eventi |
| `/var/log/auth.log` | `/var/log/auth.log` | `ro` | Log SSH *(opzionale)* |

---

### 🛡️ Sicurezza

| Area | Protezione implementata |
|------|------------------------|
| **Shell injection** | IP validato con `ipaddress.ip_address()`; jail name con regex `[a-zA-Z0-9_-]{1,64}`; path quotati con `shlex.quote()` prima di ogni comando shell |
| **XSS** | Tutti i valori API escapati con `escHtml()` prima dell'inserimento nel DOM; bottone Unban usa `data-ip` anziché `onclick` con stringa interpolata |
| **API Key auth** | Confronto a tempo costante via `secrets.compare_digest` — immune a timing attack |
| **Rate limiting** | 60 req/min per IP (configurabile); bucket scaduti rimossi automaticamente ad ogni richiesta |
| **Geo cache** | Limitata a 1024 entry con evizione FIFO |
| **SQLite** | Connessioni chiuse in blocco `try/finally` anche in caso di eccezione |
| **Docker** | Container non-root (utente `f2b`, uid 1001); solo i volumi strettamente necessari |

> **💡 Raccomandazione**: imposta sempre `F2B_API_KEY` quando esponi la web app su rete pubblica o LAN non fidata.

---

### 🔬 Note tecniche

- Il modulo condiviso `f2b_core.py` contiene tutta la logica (operazioni jail, geo, i18n, parsing log), usata sia dalla TUI che dalla web app.
- Il **tempo residuo** è letto direttamente dal database SQLite di fail2ban — preciso al secondo, non stimato.
- Il cambio ban time per singolo IP avviene in tre passi atomici: `unban → imposta nuovo bantime → re-ban → ripristina bantime originale`.
- L'indicatore **🔴 +N** segnala eventi `Found` nel log dopo l'ultimo ban — l'IP sta ancora tentando.
- Il **parsing del log è incrementale**: ad ogni refresh vengono lette solo le righe nuove dall'ultima posizione.
- **Rilevamento Synology**: se `/etc/synoinfo.conf` è presente, i percorsi dei file vengono rilevati automaticamente.
- Test: `python3 -m pytest tests/ -v` → 65 test.

---

### 📄 Licenza

**MIT** — libero di usare, modificare e distribuire.

---

<br/>

---

## 🇬🇧 English

<details>
<summary><b>📑 Table of Contents</b></summary>

- [What is it](#what-is-f2b-manager)
- [Features](#-features)
- [Prerequisites](#️-prerequisites)
- [Quick Start — TUI](#️-quick-start--tui)
- [Quick Start — Docker](#-quick-start--docker)
- [Deploy — Coolify](#-deploy--coolify)
- [Configuration](#️-configuration)
- [Security](#️-security)
- [Technical notes](#-technical-notes)

</details>

---

### What is f2b-manager?

`f2b-manager` is a complete **fail2ban management** tool with two interfaces:

<table>
<tr>
<td align="center" width="50%">

### 🖥️ TUI
Interactive terminal dashboard.<br/>
No extra dependencies, runs on any Linux.

</td>
<td align="center" width="50%">

### 🌐 Web App
Modern browser dashboard with REST API.<br/>
Docker, Coolify or bare-metal ready.

</td>
</tr>
</table>

Supports **multiple jails** (`sshd`, `synology-dsm`, `nginx-http-auth`, `postfix`, ...) and runs on **Linux** and **Synology DSM**.

---

### ✨ Features

<table>
<tr>
<th>📡 Monitoring</th>
<th>🔧 Management</th>
<th>🚀 Deploy</th>
</tr>
<tr>
<td>

🌍 IP geolocation<br/>
📊 ASCII aggressiveness bars<br/>
📈 Historical SQLite counter<br/>
🏆 All-time Top 5 IPs<br/>
🗺️ Geo distribution map<br/>
⏱️ Remaining time to the second<br/>
🔴 Active attack alerts

</td>
<td>

🔒 Ban / unban IPs<br/>
🔧 Global and per-IP ban time<br/>
🔢 Presets: 1d · 5d · 7d · 10d · 15d · 30d · ∞<br/>
↕️ Sort by IP / date / attempts<br/>
🔄 Multi-jail selector<br/>
🌐 IT / EN interface<br/>
📋 Last 20 log events

</td>
<td>

🐳 Non-root container<br/>
🧊 Coolify (one-click)<br/>
🔐 API Key auth<br/>
🛡️ Input validation & XSS protection<br/>
⏱️ Rate limiting 60 req/min<br/>
🎨 Light / dark theme<br/>
♻️ 30s auto-refresh

</td>
</tr>
</table>

---

### ⚙️ Prerequisites

| Component | Required | Notes |
|---|:---:|---|
| Linux or Synology DSM | ✅ | fail2ban must be installed and running |
| Python 3.11+ | TUI only | Not needed for Docker-based web app |
| Docker | Web only | Optional — bare metal also supported |
| geoip-bin | ❌ | Optional — enables IP geolocation |

---

### 🖥️ Quick Start — TUI

```bash
git clone https://github.com/Pier-86/f2b-manager.git
cd f2b-manager
python3 f2b-manager.py   # auto-elevates with sudo
```

**Optional environment variables:**

```bash
F2B_JAIL=sshd    # initial jail (default: sshd)
F2B_LANG=en      # language: it (default) | en
```

**Keyboard controls:**

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

### 🐳 Quick Start — Docker

```bash
docker run -d \
  --name f2b-manager-web \
  --restart unless-stopped \
  -p 8080:8080 \
  -e F2B_API_KEY=your-secret-key \
  -v /var/run/fail2ban:/var/run/fail2ban \
  -v /var/lib/fail2ban:/var/lib/fail2ban:ro \
  -v /var/log/fail2ban.log:/var/log/fail2ban.log:ro \
  pier86/f2b-manager:latest
```

Open `http://your-server:8080`.

---

### 🧊 Deploy — Coolify

> **⚠️ Key requirement**: Coolify must run on the **same server** as fail2ban. The container accesses the host's Unix socket — remote servers are not supported.

**Step 1 — New service**

In Coolify: **New Resource → Docker Compose (Empty)**

**Step 2 — Paste the Compose**

```yaml
services:
  f2b-web:
    image: pier86/f2b-manager:latest
    restart: unless-stopped
    environment:
      - F2B_JAILS=sshd
      - F2B_JAIL=sshd
      - F2B_API_KEY=${F2B_API_KEY}
      - F2B_API_RATE_LIMIT=60
      - F2B_API_RATE_WINDOW=60
    volumes:
      - /var/run/fail2ban:/var/run/fail2ban
      - /var/lib/fail2ban:/var/lib/fail2ban:ro
      - /var/log/fail2ban.log:/var/log/fail2ban.log:ro
      - /var/log/auth.log:/var/log/auth.log:ro
    ports:
      - "8080:8080"
```

**Step 3 — Environment Variables**

In the **Environment Variables** tab add:

```
F2B_API_KEY=a-long-random-secret
```

**Step 4 — Domain & HTTPS**

In the **Domains** tab add your subdomain (e.g. `f2b.yourdomain.com`).
Coolify auto-configures **Traefik + Let's Encrypt**.

**Step 5 — Deploy**

Click **Deploy** and wait. The image is pulled from Docker Hub, volumes are mounted, the service starts.

```
Internet → Traefik (Coolify) → HTTPS → f2b-manager:8080
                                              ↓
                              /var/run/fail2ban/fail2ban.sock  (host, rw)
                              /var/lib/fail2ban/fail2ban.sqlite3  (host, ro)
                              /var/log/fail2ban.log  (host, ro)
```

**Socket permission issue?**

The container runs as non-root (uid 1001). The fail2ban socket on the host is typically owned by `root:root 660`, so the container cannot reach it. Fix: add a **systemd override** on the host to widen the socket permissions on every fail2ban start:

```bash
sudo mkdir -p /etc/systemd/system/fail2ban.service.d/

sudo tee /etc/systemd/system/fail2ban.service.d/socket-perms.conf << 'EOF'
[Service]
ExecStartPost=/bin/chmod 666 /var/run/fail2ban/fail2ban.sock
EOF

sudo systemctl daemon-reload && sudo systemctl restart fail2ban
```

> This override is permanent and survives reboots.

---

### ⚙️ Configuration

**Environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `F2B_JAILS` | `sshd` | Comma-separated list of jails |
| `F2B_JAIL` | First from `F2B_JAILS` | Active jail at startup |
| `F2B_API_KEY` | *(empty)* | If set, requires auth on all API endpoints |
| `F2B_API_RATE_LIMIT` | `60` | Max requests per window |
| `F2B_API_RATE_WINDOW` | `60` | Window in seconds |
| `F2B_DB` | auto-detect | SQLite database path |
| `F2B_LOG` | auto-detect | fail2ban log path |
| `F2B_GEOIP_BIN` | `geoiplookup` | Geolocation binary |

**Required volumes:**

| Host path | Container mount | Mode | Purpose |
|-----------|----------------|:----:|---------|
| `/var/run/fail2ban` | `/var/run/fail2ban` | `rw` | Unix socket — ban/unban commands |
| `/var/lib/fail2ban` | `/var/lib/fail2ban` | `ro` | SQLite DB — remaining ban time |
| `/var/log/fail2ban.log` | `/var/log/fail2ban.log` | `ro` | Event log |
| `/var/log/auth.log` | `/var/log/auth.log` | `ro` | SSH auth log *(optional)* |

---

### 🛡️ Security

| Area | Protection |
|------|------------|
| **Shell injection** | IP validated with `ipaddress.ip_address()`; jail name checked against `[a-zA-Z0-9_-]{1,64}`; file paths quoted with `shlex.quote()` before every shell command |
| **XSS** | All API-derived values escaped with `escHtml()` before DOM insertion; Unban button uses `data-ip` attribute instead of interpolated `onclick` string |
| **API Key auth** | Constant-time comparison via `secrets.compare_digest` — immune to timing attacks |
| **Rate limiting** | 60 req/min per IP (configurable); expired buckets purged on each request to prevent unbounded memory growth |
| **Geo cache** | Capped at 1024 entries with FIFO eviction |
| **SQLite** | Connections closed in `try/finally` blocks even on exception |
| **Docker** | Non-root container (user `f2b`, uid 1001); only strictly necessary volume mounts |

> **💡 Recommendation**: always set `F2B_API_KEY` when exposing the web app on a public network or untrusted LAN.

---

### 🔬 Technical notes

- The shared module `f2b_core.py` contains all logic (jail ops, geo, i18n, log parsing), used by both TUI and web app.
- **Remaining time** is read directly from fail2ban's SQLite DB — accurate to the second, not estimated.
- Per-IP ban time change is three atomic steps: `unban → set new bantime → re-ban → restore original bantime`.
- The **🔴 +N** indicator flags `Found` log events after the last ban — the IP is still actively attacking.
- **Incremental log parsing**: only new lines are read from the last known position on each refresh.
- **Synology auto-detection**: if `/etc/synoinfo.conf` exists, file paths are probed automatically.
- Tests: `python3 -m pytest tests/ -v` → 65 tests.

---

### 📄 License

**MIT** — free to use, modify, and distribute.
