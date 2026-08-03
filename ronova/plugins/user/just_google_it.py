from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import PREFIXES, ADMIN_ID, BOT
from ..utilities import eval_helper
from ..decorators import get_string


@Client.on_message(filters.command("googleit", prefixes=PREFIXES) & filters.user(ADMIN_ID), group= 2)
@get_string("GoogleIt")
async def googleit(c: Client, m: Message):
    """
    A fun command for searching something on google
    Usage: googleit [query]
    """
    parts = m.text.split(None, 1)

    if len(parts) < 2:
        await m.reply("Usage: `.googleit <query>`")
        return

    query = parts[1].strip()
    encoded = query.replace(" ", "+")
    url = f"https://letmegooglethat.com/?q={encoded}"

    eval_helper["googleit_url"] = url

    results = await c.get_inline_bot_results(bot=BOT, query="googleit")
    await c.send_inline_bot_result(
        chat_id=m.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id,
        reply_parameters=ReplyParameters(message_id=m.id)
    )