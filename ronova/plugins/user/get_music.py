import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters
from pyrogram.errors import YouBlockedUser

from config import PREFIXES, ADMIN_ID
from ..shared import MUSIC_STATE

MUSIC_BOT:str = "MusicGotooBot"

def refresh_music_data():
    MUSIC_STATE.status = False
    MUSIC_STATE.user_chat_id = None
    MUSIC_STATE.user_message_id = None 

async def timeout_handler(m:Message):
    await asyncio.sleep(20)
    if MUSIC_STATE.status:
        m.edit("Request time out")
        refresh_music_data()

@Client.on_message(filters.command('music', prefixes=PREFIXES) & filters.user(ADMIN_ID))
async def music(c: Client, m: Message):
    if len(m.command) < 2:
        await m.reply("Usage: <code>.music &lt;music name&gt;</code>")
        return

    name = " ".join(m.command[1:])

    try:
        await c.send_message(MUSIC_BOT, name)
    except YouBlockedUser:
        await c.unblock_user(MUSIC_BOT)
        await c.send_message(MUSIC_BOT, name)

    MUSIC_STATE.status = True
    MUSIC_STATE.user_message_id = m.id
    MUSIC_STATE.user_chat_id = m.chat.id

    asyncio.create_task(timeout_handler(m))

@Client.on_edited_message(filters.user(MUSIC_BOT))
@Client.on_message(filters.user(MUSIC_BOT))
async def find_music(c: Client, m: Message):
    if not MUSIC_STATE.status:
        return

    if m.audio and m.audio.title != "⏳":
        await asyncio.sleep(2)
        await c.send_audio(MUSIC_STATE.user_chat_id, m.audio.file_id, reply_parameters=ReplyParameters(message_id=MUSIC_STATE.user_message_id))
        refresh_music_data()

    elif m.reply_markup:  
        if "🔍" in m.text:      
            await asyncio.sleep(0.5)
            try:
                await m.click(0)
            except Exception as e:
                print("Click failed:", e)
                refresh_music_data()

