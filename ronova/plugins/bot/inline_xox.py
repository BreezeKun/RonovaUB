import random

from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    InlineQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQueryResultArticle, InputTextMessageContent, CallbackQuery
)

from ..shared import XOX_DATA


def gen_board():
    if XOX_DATA.status == False:
        XOX_DATA.board = []
        row = []

        while True:
            row.append(" ")
            if len(row) == 3:
                XOX_DATA.board.append(row)
                row = []

            if len(XOX_DATA.board) == 3:
                break


def check_winner(board):
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


def gen_keyboard(user: int, target: int) -> list[list[InlineKeyboardButton]]:
    keyboard = []
    column = 0

    for i in XOX_DATA.board:
        temp_row = []
        row = 0
        for j in i:
            if j == ' ':
                temp_row.append(
                    InlineKeyboardButton(
                        " ",
                        callback_data=f"empty_{column}:{row}_{user}:{target}",
                        style=ButtonStyle.DEFAULT
                    )
                )
            elif j == "x":
                temp_row.append(
                    InlineKeyboardButton(
                        "X",
                        callback_data=f"x_{column}:{row}_{user}:{target}",
                        style=ButtonStyle.DANGER
                    )
                )
            elif j == "o":
                temp_row.append(
                    InlineKeyboardButton(
                        "O",
                        callback_data=f"o_{column}:{row}_{user}:{target}",
                        style=ButtonStyle.SUCCESS
                    )
                )
            row += 1

        keyboard.append(temp_row)
        column += 1

    return keyboard


@Client.on_inline_query(filters.regex("^xox_"))
async def inline_xox(c: Client, q: InlineQuery):
    data = q.query.split("_")

    user = int(data[1])
    target = int(data[2])

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("accept", callback_data=f"accept_{user}_{target}", style=ButtonStyle.SUCCESS),
        InlineKeyboardButton("refuse", callback_data=f"refuse_{user}_{target}", style=ButtonStyle.DANGER)
    ]])

    await q.answer([
        InlineQueryResultArticle(
            title="xox game",
            input_message_content=InputTextMessageContent(
                message_text="Game request"
            ),
            reply_markup=keyboard
        )
    ], cache_time=0)


@Client.on_callback_query(filters.regex("^(accept|refuse)"))
async def decision(c: Client, cq: CallbackQuery):
    data = cq.data.split("_")
    choice = data[0]
    user = int(data[1])
    target = int(data[2])

    if cq.from_user.id != target:
        return await cq.answer("Not allowed", show_alert=True)

    if choice == "refuse":
        await c.edit_inline_text(
            inline_message_id=cq.inline_message_id,
            text="Game request declined."
        )
    else:
        gen_board()
        XOX_DATA.status = True
        XOX_DATA.data = {
            "turn": int(random.choice([user, target])),
            user: "x",
            target: "o"
        }

        user_name = (await c.get_users(user)).first_name
        target_name = (await c.get_users(target)).first_name

        current_turn = XOX_DATA.data["turn"]
        turn_name = user_name if current_turn == user else target_name

        keyboard = gen_keyboard(user, target)

        await c.edit_inline_text(
            inline_message_id=cq.inline_message_id,
            text=f"Game started\n\nX: {user_name}\nO: {target_name}\n\nTurn: {turn_name}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


@Client.on_callback_query(filters.regex("^(empty|x|o)"))
async def mechanics(c: Client, cq: CallbackQuery):
    data = cq.data.split("_")
    choice = data[0]
    row, column = map(int, data[1].split(":"))
    user, target = map(int, data[2].split(":"))

    current_turn = XOX_DATA.data["turn"]

    if choice in ["x", "o"] or cq.from_user.id != current_turn:
        return await cq.answer("Not your turn", show_alert=True)

    XOX_DATA.board[row][column] = XOX_DATA.data[current_turn]
    XOX_DATA.data["turn"] = user if current_turn != user else target

    user_name = (await c.get_users(user)).first_name
    target_name = (await c.get_users(target)).first_name

    winner = check_winner(XOX_DATA.board)

    if winner:
        XOX_DATA.status = False
        winner_name = user_name if winner == "x" else target_name
        return await c.edit_inline_text(
            inline_message_id=cq.inline_message_id,
            text=f"Winner: {winner_name} ({winner.upper()})"
        )

    if all(cell != " " for row in XOX_DATA.board for cell in row):
        XOX_DATA.status = False
        return await c.edit_inline_text(
            inline_message_id=cq.inline_message_id,
            text="Game ended in a draw"
        )

    next_turn = XOX_DATA.data["turn"]
    turn_name = user_name if next_turn == user else target_name

    keyboard = gen_keyboard(user, target)

    await c.edit_inline_text(
        inline_message_id=cq.inline_message_id,
        text=f"X: {user_name}\nO: {target_name}\n\nTurn: {turn_name}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )