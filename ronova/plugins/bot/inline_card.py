from pyrogram import Client, filters
from pyrogram.types import (InputRichMessage, InlineQuery,
                            InlineQueryResultArticle, InputRichMessageContent,
                            CallbackQuery)

from ..utilities import fetch_data

from config import ADMIN_ID

async def build_buttons(data:dict):
    column = ""
    row = """<tg-button-row align="center">"""
    num = 0
    for name in data:
        if num > 2:
            row += """</tg-button-row>"""
            column += row
            row = """<tg-button-row align="center">"""
            num = 0
        row += f"""<tg-button type="callback_data" style="primary" data="mycard_{name}">{name}</tg-button>"""
        num += 1
    if not column.endswith("""</tg-button-row>"""):
        column += """</tg-button-row>"""

    return column
        
            

        

@Client.on_inline_query(filters.regex("mycard"))
async def inline_card(c:Client, q:InlineQuery):
    data = await fetch_data()
    button = await build_buttons(data)
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

@Client.on_callback_query(filters.regex("callback"))
async def delete_eval(c: Client, q: CallbackQuery):
    print("Hello World")