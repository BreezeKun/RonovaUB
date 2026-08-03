from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import PREFIXES, ADMIN_ID, BOT
from ..decorators import get_string


@Client.on_message(filters.command("anisearch", prefixes=PREFIXES) & filters.user(ADMIN_ID), group= 2)
@get_string("anime")
async def get_ani(c: Client, m: Message):
    """
    Search anime by name.
    Usage: anisearch [anime name]
    """
    if len(m.command) < 2:
        await m.reply("Usage: <code>.anisearch &lt;anime name&gt;</code>")
        return

    name    = " ".join(m.command[1:])
    results = await c.get_inline_bot_results(bot=BOT, query=f"anime {name}")

    await c.send_inline_bot_result(
        chat_id=m.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id,
        reply_parameters=ReplyParameters(message_id=m.id)
    )