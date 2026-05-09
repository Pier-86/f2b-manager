# f2b-manager

**Fail2ban SSH Manager — Terminal UI per la gestione dei ban SSH**

> 🇮🇹 [Italiano](#italiano) · 🇬🇧 [English](#english)

---

## Italiano

### Cos'è f2b-manager?

`f2b-manager` è uno strumento a riga di comando (TUI — Terminal User Interface) scritto in Python che ti permette di gestire **fail2ban** in modo semplice e visivo, direttamente dal terminale — senza dover ricordare comandi lunghi o scavare nei log.

fail2ban monitora i tentativi di accesso falliti (es. SSH brute-force) e banna automaticamente gli IP responsabili. `f2b-manager` ti dà una visione chiara e interattiva di tutto ciò che sta succedendo.

### Funzionalità

- **Dashboard in tempo reale** — visualizza tutti gli IP bannati con data dell'ultimo ban, tempo residuo, tentativi totali e tentativi attivi *dopo* il ban
- **Sbanna un IP** — rimuovi il ban di un indirizzo IP con un semplice numero o copiando l'IP
- **Gestione ban time** — modifica la durata del ban globale oppure per un singolo IP (unban + re-ban con nuova durata)
  - Preset pronti: 1 giorno, 5 giorni, 7 giorni, 10 giorni, 15 giorni, 30 giorni, permanente
  - Input custom: formati come `2h30m`, `5d`, `7200`, `-1` (permanente)
- **Ordinamento flessibile** — ordina la lista per: ordine originale, IP crescente, data ban (più recenti prima), numero di tentativi (più aggressivi prima)
- **Ultimi 20 eventi dal log** — visualizza gli eventi di Ban / Unban / Found con colori
- **Auto-elevazione root** — se non sei root, lo script si ri-esegue automaticamente con `sudo`

### Screenshot

```
==============================================================================
          FAIL2BAN MANAGER — SSH Protection
==============================================================================
  09/05/2026 14:32:05
==============================================================================

  Tentativi falliti totali : 1482
  IP bannati attualmente   : 5
  Ban time (default)       : 7g
  Ordinamento              : per data ban (recenti prima)

  #     IP                  Ultimo ban           Residuo     Tot  Attivi
  ----------------------------------------------------------------------
  [1 ]  203.0.113.45        2026-05-09 13:10:01  6g 22h       47  🔴 +3
  [2 ]  198.51.100.12       2026-05-08 09:44:17  5g 19h       23
  [3 ]  192.0.2.77          2026-05-07 21:05:55  4g 6h        11

  [r] Aggiorna
  [u] Sbanna un IP
  [b] Gestisci ban time
  [s] Cambia ordinamento
  [l] Ultimi eventi dal log
  [q] Esci
```

---

### Prerequisiti

- Linux (Debian/Ubuntu/CentOS/Rocky/Alma o qualsiasi distro con systemd)
- Python 3.6+
- fail2ban installato e attivo
- La jail `sshd` configurata in fail2ban

---

### 1. Installare fail2ban

#### Debian / Ubuntu

```bash
sudo apt update
sudo apt install fail2ban -y
```

#### CentOS / Rocky Linux / AlmaLinux

```bash
sudo dnf install epel-release -y
sudo dnf install fail2ban -y
```

#### Arch Linux

```bash
sudo pacman -S fail2ban
```

#### Avviare e abilitare il servizio

```bash
sudo systemctl enable --now fail2ban
sudo systemctl status fail2ban
```

---

### 2. Configurare fail2ban per SSH

fail2ban usa file `.local` per sovrascrivere i default senza toccare i file originali.

Crea il file di configurazione jail:

```bash
sudo nano /etc/fail2ban/jail.local
```

Incolla questa configurazione di base (adatta i valori alle tue esigenze):

```ini
[DEFAULT]
# Ignora sempre il tuo IP (sostituisci con il tuo)
ignoreip = 127.0.0.1/8 ::1

# Finestra di osservazione: secondi in cui contare i tentativi
findtime  = 600

# Numero massimo di tentativi prima del ban
maxretry  = 5

# Durata del ban (secondi). -1 = permanente
bantime   = 86400

[sshd]
enabled  = true
port     = ssh
logpath  = %(sshd_log)s
backend  = %(sshd_backend)s
```

Riavvia fail2ban per applicare:

```bash
sudo systemctl restart fail2ban
```

Verifica che la jail SSH sia attiva:

```bash
sudo fail2ban-client status sshd
```

---

### 3. Installare f2b-manager

#### Clona il repository

```bash
git clone https://github.com/Pier-86/f2b-manager.git
cd f2b-manager
```

#### Rendi lo script eseguibile (opzionale)

```bash
chmod +x f2b-manager.py
```

Nessuna dipendenza esterna — usa solo moduli della libreria standard Python (`subprocess`, `sqlite3`, `re`, `ipaddress`, ecc.).

---

### 4. Utilizzo

```bash
python3 f2b-manager.py
```

Lo script rileva automaticamente se non è in esecuzione come root e si ri-esegue con `sudo`.

#### Controlli da tastiera

| Tasto | Azione |
|-------|--------|
| `r`   | Aggiorna la lista |
| `u`   | Sbanna un IP (per numero o IP completo) |
| `b`   | Menu gestione ban time |
| `s`   | Cambia ordinamento |
| `l`   | Mostra ultimi 20 eventi dal log |
| `q`   | Esci |

---

### Note tecniche

- Il tempo residuo del ban viene letto direttamente dal database SQLite di fail2ban (`/var/lib/fail2ban/fail2ban.sqlite3`), quindi è preciso al secondo.
- Il cambio di ban time per singolo IP funziona con: unban → imposta nuovo bantime → re-ban → ripristina bantime originale.
- I tentativi "Attivi" (🔴 +N) indicano quanti `Found` sono stati registrati *dopo* l'ultimo ban dell'IP — un segnale che l'attacco è ancora in corso.
- Compatibile con qualsiasi sistema che abbia fail2ban con jail `sshd` attiva.

---

### Licenza

MIT License — libero di usare, modificare e distribuire.

---
---

## English

### What is f2b-manager?

`f2b-manager` is a command-line tool (TUI — Terminal User Interface) written in Python that lets you manage **fail2ban** in a simple and visual way, directly from the terminal — without having to remember long commands or dig through logs.

fail2ban monitors failed login attempts (e.g. SSH brute-force) and automatically bans the responsible IPs. `f2b-manager` gives you a clear, interactive view of everything that's happening.

### Features

- **Real-time dashboard** — displays all banned IPs with last ban date, remaining time, total attempts, and active attempts *after* the ban
- **Unban an IP** — remove the ban on an IP address using a simple number or by typing the IP
- **Ban time management** — change the global ban duration or for a single IP (unban + re-ban with new duration)
  - Ready-made presets: 1 day, 5 days, 7 days, 10 days, 15 days, 30 days, permanent
  - Custom input: formats like `2h30m`, `5d`, `7200`, `-1` (permanent)
- **Flexible sorting** — sort the list by: original order, ascending IP, ban date (most recent first), number of attempts (most aggressive first)
- **Last 20 log events** — displays Ban / Unban / Found events with color coding
- **Auto root elevation** — if you're not root, the script automatically re-runs itself with `sudo`

### Screenshot

```
==============================================================================
          FAIL2BAN MANAGER — SSH Protection
==============================================================================
  09/05/2026 14:32:05
==============================================================================

  Total failed attempts    : 1482
  Currently banned IPs     : 5
  Ban time (default)       : 7d
  Sort order               : by ban date (most recent first)

  #     IP                  Last ban             Remaining    Tot  Active
  ----------------------------------------------------------------------
  [1 ]  203.0.113.45        2026-05-09 13:10:01  6d 22h        47  🔴 +3
  [2 ]  198.51.100.12       2026-05-08 09:44:17  5d 19h        23
  [3 ]  192.0.2.77          2026-05-07 21:05:55  4d 6h         11

  [r] Refresh
  [u] Unban an IP
  [b] Manage ban time
  [s] Change sort order
  [l] Last log events
  [q] Quit
```

---

### Prerequisites

- Linux (Debian/Ubuntu/CentOS/Rocky/Alma or any systemd-based distro)
- Python 3.6+
- fail2ban installed and running
- The `sshd` jail configured in fail2ban

---

### 1. Install fail2ban

#### Debian / Ubuntu

```bash
sudo apt update
sudo apt install fail2ban -y
```

#### CentOS / Rocky Linux / AlmaLinux

```bash
sudo dnf install epel-release -y
sudo dnf install fail2ban -y
```

#### Arch Linux

```bash
sudo pacman -S fail2ban
```

#### Start and enable the service

```bash
sudo systemctl enable --now fail2ban
sudo systemctl status fail2ban
```

---

### 2. Configure fail2ban for SSH

fail2ban uses `.local` files to override defaults without touching the original files.

Create the jail configuration file:

```bash
sudo nano /etc/fail2ban/jail.local
```

Paste this basic configuration (adjust values to your needs):

```ini
[DEFAULT]
# Always ignore your own IP (replace with yours)
ignoreip = 127.0.0.1/8 ::1

# Observation window: seconds in which to count attempts
findtime  = 600

# Maximum number of attempts before banning
maxretry  = 5

# Ban duration (seconds). -1 = permanent
bantime   = 86400

[sshd]
enabled  = true
port     = ssh
logpath  = %(sshd_log)s
backend  = %(sshd_backend)s
```

Restart fail2ban to apply:

```bash
sudo systemctl restart fail2ban
```

Verify the SSH jail is active:

```bash
sudo fail2ban-client status sshd
```

---

### 3. Install f2b-manager

#### Clone the repository

```bash
git clone https://github.com/Pier-86/f2b-manager.git
cd f2b-manager
```

#### Make the script executable (optional)

```bash
chmod +x f2b-manager.py
```

No external dependencies — uses only Python standard library modules (`subprocess`, `sqlite3`, `re`, `ipaddress`, etc.).

---

### 4. Usage

```bash
python3 f2b-manager.py
```

The script automatically detects if it's not running as root and re-executes itself with `sudo`.

#### Keyboard controls

| Key | Action |
|-----|--------|
| `r` | Refresh the list |
| `u` | Unban an IP (by number or full IP) |
| `b` | Ban time management menu |
| `s` | Change sort order |
| `l` | Show last 20 log events |
| `q` | Quit |

---

### Technical notes

- Remaining ban time is read directly from fail2ban's SQLite database (`/var/lib/fail2ban/fail2ban.sqlite3`), so it is accurate to the second.
- Per-IP ban time change works as: unban → set new bantime → re-ban → restore original bantime.
- "Active" attempts (🔴 +N) indicate how many `Found` events were recorded *after* the IP's last ban — a signal that the attack is still ongoing.
- Compatible with any system that has fail2ban with the `sshd` jail active.

---

### License

MIT License — free to use, modify, and distribute.
