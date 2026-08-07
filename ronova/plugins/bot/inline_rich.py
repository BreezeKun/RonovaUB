from pyrogram import Client, filters
from pyrogram.types import (InputRichMessage, InlineQuery,
                             InlineQueryResultArticle, InputRichMessageContent)
from richparser import parse

from config import ADMIN_ID
from ..decorators import get_string

@Client.on_inline_query(filters.regex(r"rich (.+)") & filters.user(ADMIN_ID))
@get_string("rich:message")
async def inline_ani(c: Client, q: InlineQuery):
    """
    To send a rich message
    Usage: @botname rich [message]
    Note parsing is done by library richparser eg _h1:text => <h1>text</h1>
    """
    text = parse(q.matches[0].group(1))

    await q.answer([
        InlineQueryResultArticle(
            title="send rich",
            input_message_content=InputRichMessageContent(
                InputRichMessage(html=text)
            )
        )
    ], cache_time=0)