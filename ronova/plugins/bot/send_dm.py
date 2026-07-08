from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMIN_ID

@Client.on_message(filters.private)
async def send_dm(c: Client, m: Message):
    if m.from_user.id != ADMIN_ID[0]:
        await c.forward_messages(ADMIN_ID[0], m.chat.id, m.id)
    else:
        if m.from_user.id == ADMIN_ID[0]:
            if m.reply_to_message:
                try:
                    r = m.reply_to_message.forward_origin.sender_user
                    await c.send_message(r.id, m.text)
                except:
                    pass