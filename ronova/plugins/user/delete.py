import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from config import ADMIN_ID, PREFIXES
from ..decorators import get_string

command_list: list[str]= ["del","purge"]

@Client.on_message(filters.command(commands=command_list,prefixes=PREFIXES) & filters.user(ADMIN_ID), group= 2)
@get_string("delete")
async def delete(c:Client, m:Message):
    """
    Delete messages.
    Usage:
    - del → delete replied message
    - purge → delete messages up to replied message
    """

    command = m.command[0]
    r = m.reply_to_message

    try:

        if command == "del":
            """Delete a replied message"""
            await r.delete()

        elif command == "purge":
            """delete message uptil replied message"""
            rep_id = r.id
            to_id = m.id
            count = 0
            for i in range(rep_id, to_id):
                try:
                    count += await c.delete_messages(m.chat.id, i, revoke=True)
                    await asyncio.sleep(0.5)
                except:
                    pass
            await m.edit(f"total messages purged: {count}")
            await asyncio.sleep(5)
            
    except Exception as e:
        await m.edit(e)
        await asyncio.sleep(5)
    finally:
        await m.delete()
    


