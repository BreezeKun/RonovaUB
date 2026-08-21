from pyrogram import Client, filters
from pyrogram.types import Message

from config import ADMIN_ID, PREFIXES
from ..decorators import get_string
from ..utilities import MUSIC_PLAYER

@Client.on_message(filters.command("play", prefixes=PREFIXES) & filters.user(ADMIN_ID))
@get_string("play")
async def play(c:Client, m:Message):
    """
    play music in vc
    usage: play [music name]
    """
    if len(m.text) < 2:
        return await m.reply("usage: play [music]")

    music =" ".join(m.command[1:])
    MUSIC_PLAYER.add_queue(music)
    await m.reply(MUSIC_PLAYER.play_music())