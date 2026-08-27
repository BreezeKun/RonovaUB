import asyncio
import logging
import time

import uvloop

uvloop.install()

# Python 3.14 compatibility for Pyrogram
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


from pyrogram import Client
from config import API_HASH, API_ID, SESSION_STRING, BOT_TOKEN


FORMAT = "[UB]:%(message)s"

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs.txt"),
        logging.StreamHandler()
    ],
    format=FORMAT
)


ub = Client(
    "ub",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    plugins=dict(root="ronova.plugins.user")
)

bot = Client(
    "app",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="ronova.plugins.bot")
)


uptime = time.time()


def get_uptime() -> str:
    seconds = int(time.time() - uptime)

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = []

    if days:
        parts.append(f"{days}d")

    if hours:
        parts.append(f"{hours}h")

    if minutes:
        parts.append(f"{minutes}m")

    parts.append(f"{seconds}s")

    return " ".join(parts)