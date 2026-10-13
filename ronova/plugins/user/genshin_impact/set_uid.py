from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import PREFIXES, BOT, ADMIN_ID

saved_uid = [1817389136, 1816134291]
current_uid = 1817389136
@Client.on_message(filters.command("setuid",prefixes=PREFIXES) & filters.user(ADMIN_ID))
async def setuid(c:Client, m:Message):
    global current_uid
    if len(m.command) > 1:
        current_uid = int(" ".join(m.command[1:]).strip())
        return await m.reply(f"set current_uid to: {current_uid}")
    else:
        other_ids = saved_uid.remove(current_uid)
        saved_uid.append(current_uid)

        results = await c.get_inline_bot_results(bot=BOT, query = f"setuid_{other_ids}")
        await c.send_inline_bot_result(
            chat_id=m.chat.id,
            query_id=results.query_id,
            result_id=results.results[0].id,
            reply_parameters=ReplyParameters(message_id=m.id)
            )
        
