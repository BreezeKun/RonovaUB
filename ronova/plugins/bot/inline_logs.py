import os

from pyrogram import Client, filters
from pyrogram.types import (Message, ReplyParameters, InputRichMessage, 
                            InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery,
                            InlineQueryResultArticle, InputRichMessageContent,
                            InputTextMessageContent, CallbackQuery)
from pyrogram.enums import ButtonStyle

from config import ADMIN_ID
from ..filters import starts

def get_logs(data:bool = False) -> str:
    if data:
        cross = "❌"
        empty = "📭"
        board = "📋"
    else:
        emoji = "<tg-emoji emoji-id='5325888970368762082'>👅</tg-emoji>"
        cross, empty, board = emoji, emoji, emoji

    if not os.path.exists("logs.txt"):
        return f"{cross} Log file not found."
    else:
        with open("logs.txt", encoding="utf-8") as f:
            lines = f.readlines()

        tail = "".join(lines[-20:]).strip()

        if not tail:
            return f"{empty} Log file is empty."
        else:
            return f"<b>{board} Recent Logs</b>\n<pre>{tail[:4000]}</pre>"


@Client.on_inline_query(filters.regex("logs") & filters.user(ADMIN_ID))
async def inline_logs(c: Client, q: InlineQuery):

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 Clear Logs", callback_data="clear_logs", style = ButtonStyle.DANGER)]
    ])

    text = get_logs(data=True)

    await q.answer([
        InlineQueryResultArticle(
            title="📋 View Logs",
            input_message_content=InputTextMessageContent(
                text
            ),
            reply_markup=keyboard
        )
    ], cache_time=0)

@Client.on_guest_message(starts("logs") & filters.user(ADMIN_ID))
async def guest_logs(c: Client, m: Message):
    query_id = m.guest_query_id

    if m.reply_to_message:
        return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 Clear Logs", callback_data="clear_logs", style=ButtonStyle.DANGER)]
    ])

    await c.answer_guest_query(
        guest_query_id=query_id,
        result=InlineQueryResultArticle(
            title="📋 Logs",
            input_message_content=InputTextMessageContent(
                get_logs()
            ),
            reply_markup=keyboard
        )
    )
@Client.on_callback_query(filters.regex("clear_logs"))
async def clear_logs_cb(c: Client, cb:CallbackQuery):

    from config import ADMIN_ID

    if cb.from_user.id not in ADMIN_ID:
        return await cb.answer("Not allowed", show_alert=True)

    import os

    if not os.path.exists("logs.txt"):
        return await cb.answer("Log file not found", show_alert=True)

    open("logs.txt", "w").close()

    await cb.answer("Logs cleared", show_alert=True)

    await c.edit_inline_text(
        inline_message_id=cb.inline_message_id,
        text="🧹 Logs have been cleared."
    )