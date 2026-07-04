from pyrogram import Client, filters
from pyrogram.types import (InputRichMessage, InlineQuery,
                             InlineQueryResultArticle, InputRichMessageContent)
from richparser import parse

from config import ADMIN_ID

@Client.on_inline_query(filters.regex(r"rich (.+)") & filters.user(ADMIN_ID))
async def inline_ani(c: Client, q: InlineQuery):
    text = parse(q.matches[0].group(1))

    await q.answer([
        InlineQueryResultArticle(
            title="send rich",
            input_message_content=InputRichMessageContent(
                InputRichMessage(html=text)
            )
        )
    ], cache_time=0)