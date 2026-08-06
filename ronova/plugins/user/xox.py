from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, ADMIN_ID, BOT


@Client.on_message(filters.command("xox", prefixes=PREFIXES) & filters.user(ADMIN_ID))
async def xox(c: Client, m: Message):
    if not m.reply_to_message or not m.reply_to_message.from_user:
        return await m.reply_text("Reply to a user's message to challenge them.")

    user = m.from_user.id
    target = m.reply_to_message.from_user.id

    if user == target:
        return await m.reply_text("You can't challenge yourself.")


    results = await c.get_inline_bot_results(bot=BOT, query=f"xox_{user}_{target}")
    await c.send_inline_bot_result(
        chat_id=m.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id,
        reply_to_message_id=m.id
    )