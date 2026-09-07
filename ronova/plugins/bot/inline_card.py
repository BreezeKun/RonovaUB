from pyrogram import Client, filters
from pyrogram.types import (InputRichMessage, InlineQuery,
                            InlineQueryResultArticle, InputRichMessageContent,
                            CallbackQuery)

from ..utilities import fetch_data

from config import ADMIN_ID

async def build_buttons(data:dict, user_id:int):
    column = ""
    row = """<tg-button-row align="center">"""
    num = 0
    for name in data:
        if num > 2:
            row += """</tg-button-row>"""
            column += row
            row = """<tg-button-row align="center">"""
            num = 0
        row += f"""<tg-button type="callback_data" style="primary" data="mycard_{name}_{user_id}">{name}</tg-button>"""
        num += 1
    if not column.endswith("""</tg-button-row>"""):
        column += """</tg-button-row>"""

    return column
        


@Client.on_inline_query(filters.regex("mycard") & filters.user(ADMIN_ID))
async def inline_card(c:Client, q:InlineQuery):
    user_id = q.from_user.id
    data = await fetch_data()
    button = await build_buttons(data,user_id)
    await q.answer(
        [
            InlineQueryResultArticle(
                title = "builds",
                input_message_content=InputRichMessageContent(
                    InputRichMessage(
                        html = button
                    )
                )
            )
        ]
    ) 

@Client.on_callback_query(filters.regex(r"^mycard_"))
async def delete_eval(c: Client, q: CallbackQuery):
    command, name, user_id = map(str, q.data.split("_"))
    if q.from_user.id != int(user_id):
        return await q.answer("Nope", show_alert=True)
    