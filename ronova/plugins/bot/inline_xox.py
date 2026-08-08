import random
import string

from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQueryResultArticle, InputTextMessageContent, CallbackQuery,
    InlineQuery, Message
)

from ..filters import starts
from ..shared import XoxData

def gen_board(game_data):
    game_data.board = [[" " for _ in range(3)] for _ in range(3)]


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


def gen_keyboard(game_data, user, target, game_id):
    keyboard = []

    for r, row in enumerate(game_data.board):
        temp = []
        for c, cell in enumerate(row):

            text = " " if cell == " " else cell.upper()

            temp.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"{cell}_{r}:{c}_{user}:{target}_{game_id}",
                    style=ButtonStyle.DEFAULT
                )
            )

        keyboard.append(temp)

    return keyboard


@Client.on_guest_message(starts("xox"))
async def guest_xox(c: Client, m: Message):
    user = m.from_user.id
    target = m.reply_to_message.from_user.id

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("accept", callback_data=f"accept_{user}_{target}", style=ButtonStyle.SUCCESS),
        InlineKeyboardButton("refuse", callback_data=f"refuse_{user}_{target}", style=ButtonStyle.DANGER)
    ]])

    await c.answer_guest_query(
        guest_query_id=m.guest_query_id,
        result=InlineQueryResultArticle(
            title="xox game",
            input_message_content=InputTextMessageContent("Game request"),
            reply_markup=keyboard
        )
    )


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
            input_message_content=InputTextMessageContent("Game request"),
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
        return await c.edit_inline_text(
            inline_message_id=cq.inline_message_id,
            text="Game request declined."
        )

    game_id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    XoxData.add_game(game_id, XoxData())
    game_data = XoxData.players[game_id]

    gen_board(game_data)
    game_data.status = True

    game_data.data = {
        "turn": random.choice([user, target]),
        user: "x",
        target: "o"
    }

    user_name = (await c.get_users(user)).first_name
    target_name = (await c.get_users(target)).first_name

    turn = game_data.data["turn"]
    turn_name = user_name if turn == user else target_name

    keyboard = gen_keyboard(game_data, user, target, game_id)

    await c.edit_inline_text(
        inline_message_id=cq.inline_message_id,
        text=f"Game started\n\nX: {user_name}\nO: {target_name}\n\nTurn: {turn_name}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@Client.on_callback_query(filters.regex("^(empty|x|o)"))
async def mechanics(c: Client, cq: CallbackQuery):
    data = cq.data.split("_")

    choice = data[0]
    row, col = map(int, data[1].split(":"))
    user, target = map(int, data[2].split(":"))
    game_id = data[3]

    game_data = XoxData.players.get(game_id)
    if not game_data:
        return await cq.answer("Game expired", show_alert=True)

    current_turn = game_data.data["turn"]

    if choice != " " and cq.from_user.id != current_turn:
        return await cq.answer("Not your turn", show_alert=True)

    if game_data.board[row][col] != " ":
        return await cq.answer("Already taken", show_alert=True)

    game_data.board[row][col] = game_data.data[current_turn]
    game_data.data["turn"] = target if current_turn == user else user

    user_name = (await c.get_users(user)).first_name
    target_name = (await c.get_users(target)).first_name

    winner = check_winner(game_data.board)

    if winner:
        game_data.status = False
        XoxData.rem_game(game_id)

        winner_name = user_name if winner == "x" else target_name

        return await c.edit_inline_text(
            inline_message_id=cq.inline_message_id,
            text=f"Winner: {winner_name} ({winner.upper()})"
        )

    if all(cell != " " for row in game_data.board for cell in row):
        game_data.status = False
        XoxData.rem_game(game_id)

        return await c.edit_inline_text(
            inline_message_id=cq.inline_message_id,
            text="Game ended in a draw"
        )

    next_turn = game_data.data["turn"]
    turn_name = user_name if next_turn == user else target_name

    keyboard = gen_keyboard(game_data, user, target, game_id)

    await c.edit_inline_text(
        inline_message_id=cq.inline_message_id,
        text=f"X: {user_name}\nO: {target_name}\n\nTurn: {turn_name}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )