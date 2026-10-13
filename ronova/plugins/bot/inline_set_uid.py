import ast

from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

@Client.on_inline_query(filters.regex(r"^setuid_"))
async def inline_setuid(c: Client, q: InlineQuery):
    data = q.query.split("_", 1)
    saved = ast.literal_eval(data[1])

    buttons = [
        InlineKeyboardButton(
            str(saveduid),
            callback_data=f"switchuid_{saveduid}"
        )
        for saveduid in saved
    ]

    keyboard = [
        buttons[i:i + 3]
        for i in range(0, len(buttons), 3)
    ]

    result = InlineQueryResultArticle(
        title="Select UID",
        input_message_content=InputTextMessageContent(
            "Choose a UID:"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await q.answer([result], cache_time=0)


@Client.on_callback_query(filters.regex(r"^switchuid_(\d+)$"))
async def switch_uid(c: Client, q: CallbackQuery):
    global current_uid

    uid = int(q.matches[0].group(1))
    current_uid = uid

    await q.answer(f"Current UID set to {current_uid}")
    await q.edit_message_text(
        f"Current UID: `{current_uid}`"
    )