import os

from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import ADMIN_ID, PREFIXES, BOT
from ...utilities import fetch_data, pre_matching, generate_card

DOWNLOAD_DIR = "gidownloads"
IMAGE_BASE_URL = "https://ronovaub.onrender.com/images/"

@Client.on_message(
    filters.command("myc", prefixes=PREFIXES)
    & filters.user(ADMIN_ID)
)
async def mychar(c: Client, m: Message):
    data = await fetch_data()

    if len(m.command) > 1:
        name = pre_matching(
            query=" ".join(m.command[1:]).strip(),
            data=data,
        )

        if not name:
            return

        file_path = os.path.join(
            DOWNLOAD_DIR,
            f"{name}.jpg",
        )

        if os.path.exists(file_path) and data:
            caption = name

            ranking = data.get(name, {}).get("ranking")

            if ranking:
                rank = ranking.get("rank%")

                if rank is not None:
                    caption += f"\nTop: {rank}%"

            await m.reply_photo(
                photo=file_path,
                caption=caption,
            )
            return

        else:
            try:
                file_path = await generate_card(
                    name=name,
                    data=data,
                )

                if file_path is None:
                    await m.reply_text(
                        f"Character **{name}** was not found in the showcase."
                    )
                    return

                caption = name

                ranking = data.get(name, {}).get("ranking")

                if ranking:
                    rank = ranking.get("rank%")

                    if rank is not None:
                        caption += f"\nTop: {rank}%"

                image_url = (
                    f"{IMAGE_BASE_URL}"
                    f"{os.path.basename(file_path)}"
                    )

                await m.reply_photo(
                    photo=image_url,
                    caption=caption,
                )

            except Exception as e:
                await m.reply_text(
                    "Failed to generate the card.\n\n"
                    f"`{type(e).__name__}: {e}`"
                )
    else:
        results = await c.get_inline_bot_results(bot=BOT, query = "mycard")
        await c.send_inline_bot_result(
                chat_id=m.chat.id,
                query_id=results.query_id,
                result_id=results.results[0].id,
                reply_parameters=ReplyParameters(message_id=m.id)
            )