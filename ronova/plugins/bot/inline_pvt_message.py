from pyrogram import Client, filters
from pyrogram.types import (InlineQuery, InlineQueryResultArticle, InputRichMessage,
                             InputRichMessageContent, InlineKeyboardMarkup,
                             InlineKeyboardButton, CallbackQuery, Message)
from richparser import parse

from config import ADMIN_ID
from ..utilities import eval_helper

@Client.on_inline_query(filters.regex("(@\w+) (.+)"))
async def inline_whis(c: Client, q: InlineQuery):

    match = q.matches[0]

    username = match.group(1)
    text = match.group(2)

    target = await c.get_users(username)

    eval_helper[target.id] = text

    await q.answer([
        InlineQueryResultArticle(
            title="send whisper",
            input_message_content=InputRichMessageContent(
                InputRichMessage(html=parse(f"_h1:Whisper message_h3:only {target.first_name} can read"))
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("open", callback_data=f"whisper_{target.id}")
            ]])
        )
    ], cache_time=0)


@Client.on_callback_query(filters.regex(r"^whisper_(\d+)$"))
async def reveal_whisper(c: Client, cb: CallbackQuery):
    target_id = int(cb.matches[0].group(1))

    if cb.from_user.id != target_id:
        return await cb.answer("This whisper isn't for you.", show_alert=True)

    text = eval_helper.get(target_id)
    if text is None:
        return await cb.answer("This whisper has already been opened or expired.", show_alert=True)

    await cb.answer(text, show_alert=True)
    del eval_helper[target_id]

    await c.edit_inline_text(
        inline_message_id=cb.inline_message_id,
        rich_message=InputRichMessage(html=parse("_h1:Message is opened"))
    )