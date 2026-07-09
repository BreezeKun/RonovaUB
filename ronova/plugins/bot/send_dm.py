import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, MessageOriginHiddenUser, MessageOriginUser
from config import ADMIN_ID

BASE_DATA:dict = {}

@Client.on_message(filters.private)
async def send_dm(c: Client, m: Message):
    await asyncio.sleep(0.2)
    if m.from_user.id != ADMIN_ID[0]:
        await c.forward_messages(ADMIN_ID[0], m.chat.id, m.id)
        combined = f"{m.from_user.first_name or ''} {m.from_user.last_name or ''}".strip()
        if combined not in BASE_DATA:
            BASE_DATA[combined] = m.from_user.id
    else:
        if m.from_user.id == ADMIN_ID[0]:
            if m.reply_to_message:
                try:
                    r = m.reply_to_message.forward_origin

                    if isinstance(r, MessageOriginHiddenUser):
                        username = r.sender_user_name
                        _to_id = BASE_DATA.get(username)

                        if _to_id:
                            await c.forward_messages(
                                _to_id,
                                m.from_user.id,
                                m.id,
                                hide_sender_name=True
                            )
                        else:
                            print("User not found in BASE_DATA")

                    elif isinstance(r, MessageOriginUser):
                        await c.forward_messages(
                            r.sender_user.id,
                            m.from_user.id,
                            m.id,
                            hide_sender_name=True
                        )

                except Exception as e:
                    print(e)
                    print(BASE_DATA)