import os

from pyrogram import Client, filters
from pyrogram.types import (
    InputRichMessage,
    InlineQuery,
    InlineQueryResultArticle,
    InputRichMessageContent,
    CallbackQuery,
)

from ..utilities import fetch_data, generate_card
from config import ADMIN_ID


DOWNLOAD_DIR = "gidownloads"
CHAT_ID = -1003792991167

IMAGE_BASE_URL = "https://ronovaub.onrender.com/images/"


async def build_buttons(data: dict, user_id: int):
    column = ""
    row = '<tg-button-row align="center">'
    num = 0

    ln = max(map(lambda x: len(x.split()[0]), data))

    for name in data:
        if num >= 3:
            row += "</tg-button-row>"
            column += row

            row = '<tg-button-row align="center">'
            num = 0

        word = name.split()[0]
        pad = (ln - len(word)) // 2

        row += (
            '<tg-button '
            'type="callback_data" '
            'style="primary" '
            f'data="mycard_{name}_{user_id}">'
            f"{"ㅤ" * pad + word + "ㅤ" * pad}"
            "</tg-button>"
        )

        num += 1

    if num:
        row += "</tg-button-row>"
        column += row
    column += f"""<tg-button-row align="center"><tg-button type="callback_data" style="danger" data="mycardref_{user_id}_None"><b>ㅤㅤㅤㅤㅤㅤㅤㅤRefreshㅤㅤㅤㅤㅤㅤㅤㅤ</b></tg-button></tg-button-row>"""

    return column


@Client.on_inline_query(
    filters.regex("mycard") & filters.user(ADMIN_ID)
)
async def inline_card(c: Client, q: InlineQuery):
    user_id = q.from_user.id

    data = await fetch_data()

    if not data:
        return

    buttons = await build_buttons(
        data,
        user_id,
    )

    await q.answer(
        [
            InlineQueryResultArticle(
                title="Builds",
                input_message_content=InputRichMessageContent(
                    InputRichMessage(
                        html=buttons
                    )
                ),
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
            caption += f"<br>Top: {rank}%"

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

        image_url = (
            f"{IMAGE_BASE_URL}"
            f"{os.path.basename(file_path)}"
        )
        html = (
            f'<img src="{image_url}" />'
            f'<b>{caption}</b>'
            f'<tg-button-row align="center">'
            f'<tg-button '
            f'type="callback_data" '
            f'style="danger" '
            f'data="mycardback_{user_id}">'
            f"<b>ㅤㅤㅤㅤBackㅤㅤㅤㅤ</b>"
            f"</tg-button>"
            f"""><tg-button type="callback_data" style="danger" data="mycardref_{user_id}_{name}"><b>ㅤㅤㅤㅤRefreshㅤㅤㅤㅤ</b></tg-button></tg-button-row>"""
        )


        await q.edit_message_text(
            rich_message=InputRichMessage(
                html=html
            )
        )

    except Exception as e:
        print(e)

        await q.edit_message_text(
            "Failed to generate the card."
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

    buttons = await build_buttons(
        data,
        user_id,
    )

    await c.edit_inline_text(
        inline_message_id=q.inline_message_id,
        rich_message=InputRichMessage(
            html=buttons
        ),
    )
RESPONSE_FILE = os.path.join(DOWNLOAD_DIR, "response_data.json")


@Client.on_callback_query(filters.regex(r"^mycardref_"))
async def mycard_back(c: Client, q: CallbackQuery):
    _, user_id, char = q.data.split("_", 2)

    user_id = int(user_id)

    if q.from_user.id != user_id:
        return await q.answer(
            "Nope",
            show_alert=True,
        )

    if char == "None":
        if os.path.isdir(DOWNLOAD_DIR):
            for filename in os.listdir(DOWNLOAD_DIR):
                file_path = os.path.join(DOWNLOAD_DIR, filename)

                if os.path.isfile(file_path):
                    os.remove(file_path)

    else:
        for extension in (".jpg", ".jpeg", ".png"):
            file_path = os.path.join(
                DOWNLOAD_DIR,
                f"{char}{extension}",
            )

            if os.path.isfile(file_path):
                os.remove(file_path)

        if os.path.isfile(RESPONSE_FILE):
            os.remove(RESPONSE_FILE)

    await q.answer("Data refreshed")
    await q.edit_message_text("Data refreshed")