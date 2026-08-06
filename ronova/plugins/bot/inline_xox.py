from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    InlineQuery, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
)

from ..shared import XOX_DATA

def gen_board():
    if XOX_DATA.status == False:
        row = []

        while True:
            row.append("_")
            if len(row) == 3:
                XOX_DATA.board.append(row)
                row = []
                
            if len(XOX_DATA.board) == 3:
                break

def check_winner(board = XOX_DATA.board):
    for row in board:
        if row[0] == row[1] == row[2] != ' ':
            return row[0]

    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != ' ':
            return board[0][col]

    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]

    return None

@Client.on_inline_query(filters.regex("^xox_"))
async def inline_xox(c:Client, q:InlineQuery):
    data = q.query.split("_")

    print(data)

    user = data[1]
    target = data[2]

    keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("accepy", callback_data=f"accept_{user}_{target}", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("refuse", callback_data=f"refuse_{user}_{target}", style=ButtonStyle.DANGER)
        ]])

    await q.answer([
            InlineQueryResultArticle(
                title=f"xox game",
                input_message_content=InputTextMessageContent(
                    message_text="test"
                ),reply_markup=keyboard
                )
        ], cache_time=0)