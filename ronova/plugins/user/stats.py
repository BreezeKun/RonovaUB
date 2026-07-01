import time

from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import PREFIXES, ADMIN_ID, BOT
from ..utilities import eval_helper


@Client.on_message(filters.command("stats", prefixes=PREFIXES) & filters.user(ADMIN_ID))
async def stats_message(c: Client, m: Message):
    start = time.perf_counter()
    await m.reply("wait...")
    latency = round((time.perf_counter() - start) * 1000)

    eval_helper['latency'] = latency

    results = await c.get_inline_bot_results(bot=BOT, query="latency")
    await c.send_inline_bot_result(
        chat_id=m.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id,
        reply_parameters=ReplyParameters(message_id=m.id)
    )