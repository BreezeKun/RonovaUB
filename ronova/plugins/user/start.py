from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import PREFIXES, ADMIN_ID, BOT

@Client.on_message(filters.command("start",prefixes=PREFIXES) & filters.user(ADMIN_ID))
async def start(c:Client, m:Message):
    
    results = await c.get_inline_bot_results(bot=BOT, query="start")
    await c.send_inline_bot_result(
        chat_id=m.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id,
        reply_parameters=ReplyParameters(message_id=m.id)
    )