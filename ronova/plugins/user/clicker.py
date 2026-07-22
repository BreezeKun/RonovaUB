import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from ..filters import check
from..shared import PREMIUM_STATE
from config import ADMIN_ID


@Client.on_message(check() & filters.user(ADMIN_ID) , group= 0)
async def prem_click(c: Client, m: Message):

    if PREMIUM_STATE.status:
        await m.click("wait")