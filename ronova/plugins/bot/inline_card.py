import os
from pyrogram import Client, filters
from pyrogram.types import (
    Message, ReplyParameters,
    InlineQuery, CallbackQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,InputMediaPhoto
)
from pyrogram.enums import ButtonStyle

from config import PREFIXES, BOT


@Client.on_inline_query(filters.regex("^genshin_card"))
async def genshin_inline(c: Client, q: InlineQuery):
    user_id = q.from_user.id

    files = sorted(os.listdir("gi_downloads"))

    buttons = []
    row = []
    for filename in files:
        stem = os.path.splitext(filename)[0]
        char_id, _, name = stem.partition("_")
        display_name = name if name else char_id

        row.append(
            InlineKeyboardButton(
                display_name,
                callback_data=f"getcard|{char_id}|{user_id}",
                style=ButtonStyle.PRIMARY,
            )
        )
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    result = InlineQueryResultArticle(
        title="Genshin Cards",
        id="genshin_card_menu",
        input_message_content=InputTextMessageContent("**Select a character:**"),
        reply_markup=InlineKeyboardMarkup(buttons),
    )

    await q.answer([result], cache_time=0)


@Client.on_callback_query(filters.regex("^getcard\\|"))
async def send_card(c: Client, q: CallbackQuery):
    _, char_id, user_id = q.data.split("|")
    user_id = int(user_id)

    if q.from_user.id != user_id:
        return await q.answer("Not your", show_alert=True)

    match = next(
        (f for f in os.listdir("gi_downloads") if f.startswith(f"{char_id}_") or f == f"{char_id}.png"),
        None,
    )
    if not match:
        return await q.answer("File not found", show_alert=True)

    await q.answer()

    path = os.path.join("gi_downloads", match)
    await c.edit_inline_media(
        inline_message_id=q.inline_message_id,
        media=InputMediaPhoto(path),
    )