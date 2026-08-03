from dataclasses import dataclass, field

from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from pyrogram.enums import ButtonStyle

from config import ADMIN_ID
from ..shared import HELP_STORAGE


@dataclass
class CreateGrid:
    grid: dict[str, list[list[InlineKeyboardButton]]] = field(default_factory=dict)

    def gen_board(self, data: dict[str, str], user_id: int):
        block = []
        row = []
        num = 1

        for key in data:
            row.append(
                InlineKeyboardButton(
                    text=key,
                    callback_data=f"help_{key}_{user_id}",
                    style=ButtonStyle.PRIMARY
                )
            )

            if len(row) == 3:
                block.append(row)
                row = []

            if len(block) == 2:
                self.grid[f"data_{num}"] = block
                block = []
                num += 1

        if row:
            block.append(row)

        if block:
            self.grid[f"data_{num}"] = block

        return self.grid


def build_keyboard(data, page: int, user_id: int):
    keys = list(data.keys())
    total = len(keys)

    current = data[keys[page]].copy()

    nav = []

    if page > 0:
        nav.append(
            InlineKeyboardButton("<", callback_data=f"helpnav_{page-1}_{user_id}", style=ButtonStyle.DANGER)
        )

    if page < total - 1:
        nav.append(
            InlineKeyboardButton(">", callback_data=f"helpnav_{page+1}_{user_id}", style=ButtonStyle.DANGER)
        )

    if nav:
        current.append(nav)

    return InlineKeyboardMarkup(current)


@Client.on_inline_query(filters.regex("^help$") & filters.user(ADMIN_ID))
async def inline_help(c: Client, q: InlineQuery):

    help_data = HELP_STORAGE.data
    user_id = q.from_user.id

    create_data = CreateGrid()
    grid_data = create_data.gen_board(help_data, user_id)

    keyboard = build_keyboard(grid_data, 0, user_id)

    await q.answer([
        InlineQueryResultArticle(
            title="Help Menu",
            description="Click to open help",
            input_message_content=InputTextMessageContent("Help Menu"),
            reply_markup=keyboard
        )
    ], cache_time=0)


@Client.on_callback_query(filters.regex("^helpnav_"))
async def help_page_handler(c: Client, q: CallbackQuery):

    data = q.data.split("_")
    page = int(data[1])
    owner_id = int(data[2])

    if q.from_user.id != owner_id:
        return await q.answer("Access denied", show_alert=True)

    help_data = HELP_STORAGE.data

    create_data = CreateGrid()
    grid_data = create_data.gen_board(help_data, owner_id)

    keyboard = build_keyboard(grid_data, page, owner_id)

    await c.edit_inline_reply_markup(
        inline_message_id=q.inline_message_id,
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex("^help_"))
async def help_handler(c: Client, q: CallbackQuery):

    data = q.data.split("_")
    query = data[1]
    owner_id = int(data[2])

    if q.from_user.id != owner_id:
        return await q.answer("Access denied", show_alert=True)

    help_data = HELP_STORAGE.data


    await c.edit_inline_text(
        inline_message_id=q.inline_message_id,
        text= help_data[query]
    )