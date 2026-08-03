from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import ADMIN_ID, BOT, PREFIXES
from ..utilities import get_output, eval_helper
from ..decorators import get_string


@Client.on_message(filters.command("e", prefixes=PREFIXES) & filters.user(ADMIN_ID), group= 2)
@get_string("eval")
async def cmd_exec_python(c:Client, m:Message):
    """
    Evaluvate a code
    Usage: e <executable code>
    """

    parts = m.text.split(None, 1)
    if len(parts) == 1:
        text = "No code provided."

    else:
        text = await get_output(parts, c, m)

    eval_helper["result"] = text
    eval_helper["code"] = parts[1] if len(parts)>1 else "No code provided."
    eval_helper["chat_id"] = m.chat.id


    results = await c.get_inline_bot_results(bot=BOT, query="eval")
    x = await c.send_inline_bot_result(
        chat_id=m.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id,
        reply_parameters=ReplyParameters(message_id=m.id)
    )
    eval_helper['message_id'] = x.id
    eval_helper['sent_id'] = m.id