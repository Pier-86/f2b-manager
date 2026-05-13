import os
import re
import time
import logging
import secrets
import ipaddress
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from f2b_core import (
    Config, F2BError, get_jail_status, get_jail_bantime, set_jail_bantime,
    unban_ip, get_remaining_bantimes, get_historical_count, get_ip_stats,
    get_geo, get_available_jails,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("f2b-web")

config = Config()

_rate_limit_buckets: dict[str, dict] = {}
_JAIL_RE = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')


def _checked_ip(ip: str) -> str:
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid IP address: {ip!r}")


def _checked_jail(jail: str) -> str:
    if not _JAIL_RE.match(jail):
        raise HTTPException(status_code=400, detail=f"Invalid jail name: {jail!r}")
    return jail


def _check_rate_limit(request: Request):
    if not config.API_RATE_LIMIT:
        return
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    expired = [k for k, v in _rate_limit_buckets.items()
               if now - v["window_start"] > config.API_RATE_WINDOW]
    for k in expired:
        del _rate_limit_buckets[k]
    bucket = _rate_limit_buckets.get(client_ip)
    if bucket is None or now - bucket["window_start"] > config.API_RATE_WINDOW:
        bucket = {"tokens": config.API_RATE_LIMIT - 1, "window_start": now}
        _rate_limit_buckets[client_ip] = bucket
    else:
        if bucket["tokens"] <= 0:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        bucket["tokens"] -= 1


async def verify_auth(request: Request):
    if not config.API_KEY:
        return
    key = request.headers.get("X-API-Key", "")
    if not secrets.compare_digest(key, config.API_KEY):
        raise HTTPException(status_code=401, detail="Unauthorized — missing or invalid X-API-Key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    available = get_available_jails()
    logger.info("f2b-manager web starting — jails: %s", [j["jail"] for j in available])
    if config.API_KEY:
        logger.info("API key auth enabled")
    platform = "synology" if os.path.exists("/etc/synoinfo.conf") else "linux"
    logger.info("Platform: %s", platform)
    yield
    logger.info("f2b-manager web stopped")


app = FastAPI(title="f2b-manager Web", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def format_duration(seconds: int) -> str:
    if seconds == -1:
        return "Permanente"
    if seconds == 0:
        return "Scaduto"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


# ── API endpoints ──────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/jails")
async def api_jails(_=Depends(verify_auth), __=Depends(_check_rate_limit)):
    jails = get_available_jails()
    return {
        "jails": jails,
        "active": config.ACTIVE_JAIL,
        "platform": "synology" if os.path.exists("/etc/synoinfo.conf") else "linux",
    }


@app.get("/api/status")
async def api_status(jail: str = Query(None), _=Depends(verify_auth), __=Depends(_check_rate_limit)):
    j = _checked_jail(jail or config.ACTIVE_JAIL)
    try:
        status = get_jail_status(j, config)
    except F2BError as e:
        logger.error("get_status(%s) failed: %s", j, e)
        raise HTTPException(status_code=503, detail=f"fail2ban jail '{j}' not reachable")

    ips = status["banned_ips"]
    remaining = get_remaining_bantimes(ips, j, config)
    ip_stats = get_ip_stats(ips, j, config)
    historical = get_historical_count(j, config)
    bantime_seconds = get_jail_bantime(j, config)

    bans = []
    for ip in ips:
        cc, country = get_geo(ip, config)
        rem = remaining.get(ip, 0)
        st = ip_stats.get(ip, {})
        bans.append({
            "ip": ip,
            "country_code": cc,
            "country": country,
            "remaining_seconds": rem,
            "remaining_label": format_duration(rem),
            "total_found": st.get("total_found", 0),
            "last_ban": st.get("ban_time"),
        })

    bans.sort(key=lambda x: x["remaining_seconds"] if x["remaining_seconds"] != -1 else 999_999_999, reverse=True)

    jails_meta = get_available_jails()
    jail_info = next((jf for jf in jails_meta if jf["jail"] == j), {"jail": j, "name": j, "icon": "\U0001f6e1\ufe0f"})

    return {
        "jail": j,
        "jail_name": jail_info.get("name", j),
        "jail_icon": jail_info.get("icon", "\U0001f6e1\ufe0f"),
        "banned_count": len(ips),
        "total_failed": status["total_failed"],
        "total_banned_ever": status["total_banned"],
        "historical_unique": historical,
        "bantime_seconds": bantime_seconds,
        "bantime_label": format_duration(bantime_seconds),
        "bans": bans,
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.post("/api/unban/{ip}")
async def api_unban(ip: str, jail: str = Query(None), _=Depends(verify_auth), __=Depends(_check_rate_limit)):
    _checked_ip(ip)
    j = _checked_jail(jail or config.ACTIVE_JAIL)
    try:
        ok = unban_ip(ip, j, config)
    except F2BError as e:
        logger.warning("unban %s from %s failed: %s", ip, j, e)
        raise HTTPException(status_code=400, detail=str(e))
    if ok:
        logger.info("unbanned %s from %s", ip, j)
        return {"success": True, "ip": ip, "jail": j}
    raise HTTPException(status_code=400, detail="Unban failed")


class BantimeRequest(BaseModel):
    seconds: int


@app.get("/api/bantime")
async def api_get_bantime(jail: str = Query(None), _=Depends(verify_auth), __=Depends(_check_rate_limit)):
    j = _checked_jail(jail or config.ACTIVE_JAIL)
    raw = get_jail_bantime(j, config)
    return {"seconds": raw, "label": format_duration(raw), "jail": j}


@app.post("/api/bantime")
async def api_set_bantime(body: BantimeRequest, jail: str = Query(None), _=Depends(verify_auth), __=Depends(_check_rate_limit)):
    j = _checked_jail(jail or config.ACTIVE_JAIL)
    if body.seconds < 60:
        raise HTTPException(status_code=400, detail="Minimum bantime is 60 seconds")
    try:
        set_jail_bantime(body.seconds, j, config)
    except F2BError as e:
        logger.error("set bantime on %s failed: %s", j, e)
        raise HTTPException(status_code=500, detail=str(e))
    logger.info("bantime on %s set to %ds", j, body.seconds)
    return {"success": True, "seconds": body.seconds, "label": format_duration(body.seconds), "jail": j}
