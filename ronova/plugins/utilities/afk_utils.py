import time
import asyncio

from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.enums import MessageMediaType

from ..shared import AFK_DATA


def refresh_data():
    AFK_DATA.status = False
    AFK_DATA.reason = None
    AFK_DATA.afk_time = None
    AFK_DATA.file_id = None
    AFK_DATA.file_type = None
    AFK_DATA.media_from_chat = None
    AFK_DATA.message_media_id = None
    AFK_DATA.users.clear()


def format_time(seconds: int) -> str:
    if seconds < 1:
        return "just now"

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s:
        parts.append(f"{s}s")

    return " ".join(parts)


def extract_media(message:Message):
    if not message or not message.media:
        return None, None

    media = message.media

    if media == MessageMediaType.ANIMATION:
        return message.animation.file_id, "animation"
    if media == MessageMediaType.AUDIO:
        return message.audio.file_id, "audio"
    if media == MessageMediaType.PHOTO:
        return message.photo.file_id, "photo"
    if media == MessageMediaType.STICKER:
        return message.sticker.file_id, "sticker"
    if media == MessageMediaType.VIDEO:
        return message.video.file_id, "video"
    if media == MessageMediaType.VOICE:
        return message.voice.file_id, "voice"
    if media == MessageMediaType.DOCUMENT:
        return message.document.file_id, "document"

    return None, None


async def send(c, m, text: str):
    repl = None

    try:
        if AFK_DATA.file_id and AFK_DATA.file_type:
            t = AFK_DATA.file_type

            if t == "photo":
                repl = await m.reply_photo(AFK_DATA.file_id, caption=text)
            elif t == "video":
                repl = await m.reply_video(AFK_DATA.file_id, caption=text)
            elif t == "animation":
                repl = await m.reply_animation(AFK_DATA.file_id, caption=text)
            elif t == "audio":
                repl = await m.reply_audio(AFK_DATA.file_id, caption=text)
            elif t == "voice":
                repl = await m.reply_voice(AFK_DATA.file_id)
            elif t == "document":
                repl = await m.reply_document(AFK_DATA.file_id, caption=text)
            elif t == "sticker":
                sticker = await m.reply_sticker(AFK_DATA.file_id)
                repl = await m.reply_text(text)
                await asyncio.sleep(5)
                await sticker.delete()

        else:
            repl = await m.reply_text(text)
        await asyncio.sleep(5)
        
        if repl:
            await repl.delete()

    except Exception as e:
        print(e)

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send(c, m, text)
