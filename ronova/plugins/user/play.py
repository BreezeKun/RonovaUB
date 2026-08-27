import asyncio
from pytgcalls.types import MediaStream


from pyrogram import Client, filters
from pyrogram.types import Message

from config import ADMIN_ID, PREFIXES
from ..decorators import get_string
from ..utilities import MUSIC_PLAYER, VOICE_PLAYER

@Client.on_message(filters.command("play", prefixes=PREFIXES) & filters.user(ADMIN_ID))
@get_string("play")
async def play(c:Client, m:Message):
    """
    play music in vc
    usage: play [music name]
    """
    if len(m.command) < 2:
        return await m.reply(
            "Usage: /play [music]"
        )

    music = " ".join(m.command[1:])

    MUSIC_PLAYER.add_queue(music)

    # If already playing, just add to queue
    if VOICE_PLAYER.playing:
        position = len(MUSIC_PLAYER.queue)

        return await m.reply(
            f"🎵 Added to queue\n"
            f"**{music}**\n"
            f"Position: `{position}`"
        )

    # User's current group
    chat_id = m.chat.id

    VOICE_PLAYER.chat_id = chat_id

    msg = await m.reply(
        f"🔎 Searching for `{music}`..."
    )

    song = await asyncio.to_thread(
        MUSIC_PLAYER.get_next
    )

    if not song:
        return await msg.edit(
            "❌ Song not found."
        )

    VOICE_PLAYER.current = song
    VOICE_PLAYER.playing = True

    await msg.edit(
        f"🎵 **{song['title']}**\n"
        f"👤 {song['artist']}\n"
        f"⏱ {song['duration_string']}"
    )

    await VOICE_PLAYER.call.play(
        chat_id,
        MediaStream(song["filename"])
    )