import os
import json
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from enkard.enka import GenshinClient, gi
from enkard.enkacard.encbanner import CreateBanner
from enkard.enkacard.utils.create_banner_one import generationOne

from config import ADMIN_ID, PREFIXES, GI_UID, BOT


DOWNLOAD_DIR = "gidownloads"
RESPONSE_FILE = os.path.join(DOWNLOAD_DIR, "response_data.json")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

custom_image = {
    "Skirk": "https://ik.imagekit.io/cocogoat/1352449904-10000114_WWvIz_L1L",
    "Odette": "https://files.catbox.moe/w1tgs5.jpg",
    "Mavuika": "https://files.catbox.moe/fojcvc.jpg",
    "Escoffier": "https://files.catbox.moe/i29ary.jpg",
    "Arlecchino": "https://files.catbox.moe/vlid2p.jpg",
}


def pre_matching(query: str, data: dict):
    query = query.lower().strip()

    for character_name in data:
        words = character_name.lower().split()

        if any(word.startswith(query) for word in words):
            return character_name

    return None


async def fetch_data():
    if os.path.isfile(RESPONSE_FILE):
        try:
            with open(RESPONSE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        except (json.JSONDecodeError, OSError):
            return None

    try:
        async with GenshinClient(gi.Language.ENGLISH) as api:
            response = await api.fetch_showcase(GI_UID)
            data = response.model_dump()

        response_data = CreateBanner(
            data=data,
            custom_image=custom_image,
            akasha=True,
        ).generate()

        with open(RESPONSE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                response_data,
                f,
                indent=4,
                ensure_ascii=False,
            )

        return response_data

    except Exception:
        raise


async def generate_card(name: str, data: dict):
    if name not in data:
        return None

    character_data = data[name]

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{name}.jpg",
    )

    if character_data.get("custom_image"):
        banner = await generationOne(
            character_data,
            adapt=True,
        )
    else:
        banner = await generationOne(
            character_data,
        )

    banner = banner.convert("RGB")

    banner.save(
        file_path,
        "JPEG",
        quality=55,
        optimize=True,
    )

    return file_path


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

                await m.reply_photo(
                    photo=file_path,
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