from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery, InlineQueryResultArticle,
    InputRichMessage, InputRichMessageContent
)

from ..utilities import eval_helper , ADMIN_ID


@Client.on_inline_query(filters.regex(r"^think (.+)") & filters.user(ADMIN_ID))
async def inline_think(c: Client, q: InlineQuery):
    key = q.matches[0].group(1)

    html = eval_helper.get(key, "<p>Expired or not found</p>")

    await q.answer([
        InlineQueryResultArticle(
            title="Think Result",
            description="AI Generated Answer",
            input_message_content=InputRichMessageContent(
                InputRichMessage(html=html[:4000])
            )
        )
    ], cache_time=0)