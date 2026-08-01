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

from config import ADMIN_ID
from ..shared import HELP_STORAGE

@dataclass
class CreateGrid:
    grid: dict[str, list[list[InlineKeyboardButton]]] = field(default_factory=dict)

    def gen_board(self, data: dict[str, str]):
        block = []
        row = []
        num = 1

        for key in data:
            row.append(
                InlineKeyboardButton(text=key, callback_data=f"help_{key}")
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


def build_keyboard(data, page: int):
    keys = list(data.keys())
    total = len(keys)

    current = data[keys[page]].copy()

    nav = []

    if page > 0:
        nav.append(InlineKeyboardButton("<", callback_data=f"help_page_{page-1}"))

    if page < total - 1:
        nav.append(InlineKeyboardButton(">", callback_data=f"help_page_{page+1}"))

    if nav:
        current.append(nav)

    return InlineKeyboardMarkup(current)


@Client.on_inline_query(filters.regex("^help$") & filters.user(ADMIN_ID))
async def inline_help(c: Client, q: InlineQuery):

    help_data = HELP_STORAGE.data

    create_data = CreateGrid()
    grid_data = create_data.gen_board(help_data)

    keyboard = build_keyboard(grid_data, 0)

    await q.answer([
        InlineQueryResultArticle(
            title="Help Menu",
            description="Click to open help",
            input_message_content=InputTextMessageContent("Help Menu"),
            reply_markup=keyboard
        )
    ], cache_time=0)


@Client.on_callback_query(filters.regex("^help_page_"))
async def help_page_handler(c: Client, q: CallbackQuery):

    page = int(q.data.split("_")[-1])

    help_data = HELP_STORAGE.data

    create_data = CreateGrid()
    grid_data = create_data.gen_board(help_data)

    keyboard = build_keyboard(grid_data, page)

    await q.message.edit_reply_markup(reply_markup=keyboard)