from pyrogram import Client, filters
from pyrogram.types import Message

from config import ADMIN_ID, PREFIXES

@Client.on_message(filters.command("del",prefixes=PREFIXES) & filters.user(ADMIN_ID))
async def delete(c:Client, m:Message):
    r = m.reply_to_message
    try:
        await r.delete()
    finally:
        await m.delete()