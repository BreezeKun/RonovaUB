from pyrogram import Client, filters
from pyrogram .types import Message, ReplyParameters

from config import PREFIXES, ADMIN_ID
from ..utilities import get_target_id
from ..shared import HIS_STATE

HIS_BOT = "SangMata_BOT"

@Client.on_message(filters.command("history", prefixes=PREFIXES) & filters.user(ADMIN_ID))
async def sang_history(c:Client, m:Message):
    TARGET_ID = await get_target_id(c, m)
    x = await c.send_message(HIS_BOT, TARGET_ID)
    HIS_STATE.status = True
    HIS_STATE.user_chat_id = m.chat.id
    HIS_STATE.user_message_id = x.id

@Client.on_edited_message(filters.user(HIS_BOT))
@Client.on_message(filters.user(HIS_BOT))
async def find_HIS(c: Client, m: Message):
    if not HIS_STATE.status:
        return

    if m.text and m.text.startswith("👤 History for"):
        text = await m.copy(m.chat.id).text()

        await c.send_message(
                chat_id = HIS_STATE.user_chat_id, 
                text=text, 
                reply_parameters= ReplyParameters(message_id = HIS_STATE.user_message_id)
                )
    HIS_STATE.status = False
    HIS_STATE.user_chat_id = None
    HIS_STATE.user_message_id = None