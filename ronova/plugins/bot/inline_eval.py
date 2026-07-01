from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,CallbackQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.enums import ButtonStyle

from ..utilities import eval_helper,paste
from config import ADMIN_ID

@Client.on_inline_query(filters.regex("eval") & filters.user(ADMIN_ID))
async def inline_eval(c: Client, q: InlineQuery):
    user_id = q.from_user.id

    text = eval_helper.get("result", "No Text")
    code = eval_helper.get("code", "No code")

    buttons = [
        [InlineKeyboardButton("Delete", callback_data=f"del_{user_id}", style=ButtonStyle.DANGER)]
    ]

    if len(text) > 300:
        link = await paste.create(
            content=text,
        )
        eval_helper["paste_id"] = link[17::]
        buttons.append(
            [InlineKeyboardButton("Full Output", url=link, style=ButtonStyle.PRIMARY)]
        )
        text = f"Output too long, click button below\nBin_id: {eval_helper["paste_id"]}"

    await q.answer(
        [
            InlineQueryResultArticle(
                title="Eval Output",
                input_message_content=InputTextMessageContent(
                    f"**Code:**\n```python\n{code}```\n\n"
                    f"**Output:**\n<blockquote>{text}</blockquote>"
                ),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        ],
        cache_time=0
    )

@Client.on_callback_query(filters.regex("^del_"))
async def delete_eval(c: Client, q: CallbackQuery):
    user_id = int(q.data.split("_")[1])
    if q.from_user.id != user_id:
        return await q.answer("Not your", show_alert=True)

    await q.answer("Deleted")

    paste_id = eval_helper.get("paste_id")
    if paste_id:
        await paste.delete(paste_id)

    from ronova import ub
    try:
        await ub.delete_messages(
            chat_id=eval_helper['chat_id'],
            message_ids=[eval_helper['message_id'], eval_helper['sent_id']]
        )
    except Exception as e:
        print(f"Delete failed: {e}")

    eval_helper.clear()