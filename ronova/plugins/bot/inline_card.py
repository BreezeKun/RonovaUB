import os

from pyrogram import Client, filters
from pyrogram.types import (
    InputRichMessage,
    InlineQuery,
    InlineQueryResultArticle,
    InputRichMessageContent,
    CallbackQuery,
    InputMediaPhoto,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from ..utilities import fetch_data, generate_card
from config import ADMIN_ID


DOWNLOAD_DIR = "gidownloads"


async def build_buttons(data: dict, user_id: int):
    column = ""
    row = """<tg-button-row align="center">"""
    num = 0

    for name in data:
        if num >= 3:
            row += """</tg-button-row>"""
            column += row
            row = """<tg-button-row align="center">"""
            num = 0

        row += (
            f"""<tg-button type="callback_data" """
            f"""style="primary" """
            f"""data="mycard_{name}_{user_id}">{name}</tg-button>"""
        )

        num += 1

    if num:
        row += """</tg-button-row>"""
        column += row

    return column


@Client.on_inline_query(filters.regex("mycard") & filters.user(ADMIN_ID))
async def inline_card(c: Client, q: InlineQuery):
    user_id = q.from_user.id

    data = await fetch_data()

    if not data:
        return

    button = await build_buttons(data, user_id)

    await q.answer(
        [
            InlineQueryResultArticle(
                title="builds",
                input_message_content=InputRichMessageContent(
                    InputRichMessage(
                        html=button
                    )
                )
            )
        ]
    )


@Client.on_callback_query(filters.regex(r"^mycard_"))
async def mycard_callback(c: Client, q: CallbackQuery):
    _, name, user_id = q.data.split("_", 2)

    user_id = int(user_id)

    if q.from_user.id != user_id:
        return await q.answer(
            "Nope",
            show_alert=True,
        )

    await q.answer()

    await q.edit_message_text("Please wait...")

    data = await fetch_data()

    if not data:
        return await q.edit_message_text(
            "Failed to fetch showcase data."
        )

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{name}.jpg",
    )

    caption = name

    ranking = data.get(name, {}).get("ranking")

    if ranking:
        rank = ranking.get("rank%")

        if rank is not None:
            caption += f"\nTop: {rank}%"

    try:
        if not os.path.exists(file_path):
            file_path = await generate_card(
                name=name,
                data=data,
            )

            if file_path is None:
                return await q.edit_message_text(
                    f"Character {name} was not found in the showcase."
                )

        await q.edit_message_media(
            media=InputMediaPhoto(
                media=file_path,
                caption=caption,
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Back",
                            callback_data=f"mycardback_{user_id}",
                        )
                    ]
                ]
            ),
        )

    except Exception as e:
        await q.edit_message_text(
            f"Failed to generate the card: {type(e).__name__}: {e}"
        )


@Client.on_callback_query(filters.regex(r"^mycardback_"))
async def mycard_back(c: Client, q: CallbackQuery):
    _, user_id = q.data.split("_", 1)

    user_id = int(user_id)

    if q.from_user.id != user_id:
        return await q.answer(
            "Nope",
            show_alert=True,
        )

    await q.answer()

    data = await fetch_data()

    if not data:
        return await q.edit_message_text(
            "Failed to fetch showcase data."
        )

    button = await build_buttons(
        data,
        user_id,
    )

    await c.edit_inline_text(
        inline_message_id=q.inline_message_id,
        rich_message=InputRichMessage(
            html=button
        ),
    )