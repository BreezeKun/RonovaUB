from pyrogram import Client
from pyrogram.types import Message

async def get_target_id(c:Client, m:Message) -> int:
    try:
        if m.reply_to_message and m.reply_to_message.from_user.id != m.from_user.id:
            return m.reply_to_message.from_user.id

        elif len(m.command) > 1:
            arg = m.command[1]
            user = await c.get_users(arg)
            return user.id
    except Exception as e:
        print(e)