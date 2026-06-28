import time

from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from ..utilities import eval_helper
from config import ADMIN_ID


@Client.on_inline_query(filters.regex("googleit") & filters.user(ADMIN_ID))
async def inline_googleit(c: Client, q: InlineQuery):


    start = time.perf_counter()
    await q.answer([
        InlineQueryResultArticle(
            title="I've googled it for you",
            input_message_content=InputTextMessageContent(
                f"wait"
            )
        )
    ], cache_time=0)