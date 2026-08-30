import os
import json

from pyrogram import Client, filters
from pyrogram.types import Message

from enkard.enka import GenshinClient, gi
from enkard.enkacard.encbanner import CreateBanner
from enkard.enkacard.utils.create_banner_one import generationOne

from config import ADMIN_ID, PREFIXES


UID = 1817389136

DOWNLOAD_DIR = "gidownloads"
RESPONSE_FILE = os.path.join(DOWNLOAD_DIR, "response_data.json")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def generate_character_card(name: str):
    """
    Generate a character card.

    Returns:
        tuple[str | None, dict]:
            file path and response data.
    """

    # Fetch showcase
    async with GenshinClient(gi.Language.ENGLISH) as client:
        response = await client.fetch_showcase(UID)
        data = response.model_dump()

    # Generate banner data
    response_data = CreateBanner(
        data=data,
        custom_image={
            "Skirk": "https://ik.imagekit.io/cocogoat/1352449904-10000114_WWvIz_L1L",
            "Odette": "https://files.catbox.moe/w1tgs5.jpg",
            "Mavuika": "https://files.catbox.moe/fojcvc.jpg",
            "Escoffier": "https://files.catbox.moe/i29ary.jpg",
        },
        akasha=False
    ).generate()

    # Save response_data to JSON
    with open(RESPONSE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            response_data,
            f,
            indent=4,
            ensure_ascii=False,
        )

    # Find character case-insensitively
    character_data = None
    actual_name = None

    for char_name, char_data in response_data.items():
        if char_name.lower() == name.lower():
            character_data = char_data
            actual_name = char_name
            break

    if character_data is None:
        return None, response_data

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{actual_name.lower()}.png",
    )

    banner = await generationOne(
        character_data,
        adapt=False,
        lvl="Level",
        uid=str(UID),
        hide_uid=False,
    )

    banner.save(file_path)

    return file_path, response_data


def get_cached_response_data():
    """
    Load cached response_data.json.
    """

    if not os.path.isfile(RESPONSE_FILE):
        return None

    try:
        with open(RESPONSE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def get_character_data(response_data: dict, name: str):
    """
    Find character data case-insensitively.

    Returns:
        tuple[str | None, dict | None]
    """

    for char_name, char_data in response_data.items():
        if char_name.lower() == name.lower():
            return char_name, char_data

    return None, None


@Client.on_message(
    filters.command("myc", prefixes=PREFIXES)
    & filters.user(ADMIN_ID)
)
async def myc_command(client: Client, message: Message):

    # /myc odette
    if len(message.command) < 2:
        await message.reply_text(
            "Usage:\n"
            "/myc <character>\n\n"
            "Example:\n"
            "/myc odette"
        )
        return

    name = " ".join(message.command[1:]).strip()

    # First try to find the character in cached JSON
    response_data = get_cached_response_data()

    actual_name = None
    character_data = None

    if response_data:
        actual_name, character_data = get_character_data(
            response_data,
            name,
        )

    # If JSON exists and character exists, use actual character name
    if actual_name:
        file_path = os.path.join(
            DOWNLOAD_DIR,
            f"{actual_name.lower()}.png",
        )
    else:
        file_path = os.path.join(
            DOWNLOAD_DIR,
            f"{name.lower()}.png",
        )

    # Already generated
    if os.path.exists(file_path) and response_data:
        caption = actual_name or name.title()

        ranking = character_data.get("ranking") if character_data else None

        if ranking:
            rank = ranking.get("rank%")

            if rank is not None:
                caption += f"\nTop: {rank}"

        await message.reply_photo(
            photo=file_path,
            caption=caption,
        )
        return

    # Generate
    status = await message.reply_text(
        f"Generating **{name.title()}**..."
    )

    try:
        file_path, response_data = await generate_character_card(name)

        if file_path is None:
            await status.edit_text(
                f"Character **{name.title()}** was not found "
                "in the showcase."
            )
            return

        # Get the actual character name from response_data
        actual_name, character_data = get_character_data(
            response_data,
            name,
        )

        caption = actual_name or name.title()

        # Get ranking
        ranking = (
            character_data.get("ranking")
            if character_data
            else None
        )

        if ranking:
            rank = ranking.get("rank%")

            if rank is not None:
                caption += f"\nTop: {rank}"

        await status.delete()

        await message.reply_photo(
            photo=file_path,
            caption=caption,
        )

    except Exception as e:
        await status.edit_text(
            "Failed to generate the card.\n\n"
            f"`{type(e).__name__}: {e}`"
        )


@Client.on_message(
    filters.command("girefresh", prefixes=PREFIXES)
    & filters.user(ADMIN_ID)
)
async def girefresh_command(client: Client, message: Message):

    if len(message.command) < 2:
        await message.reply_text(
            "Usage:\n"
            "/girefresh <character>\n\n"
            "Example:\n"
            "/girefresh odette"
        )
        return

    name = " ".join(message.command[1:]).strip().lower()

    deleted = False

    # Delete character image
    for extension in (".jpg", ".jpeg", ".png"):
        file_path = os.path.join(
            DOWNLOAD_DIR,
            f"{name}{extension}",
        )

        if os.path.isfile(file_path):
            os.remove(file_path)
            deleted = True

    # Delete response JSON
    if os.path.isfile(RESPONSE_FILE):
        os.remove(RESPONSE_FILE)
        deleted = True

    if deleted:
        await message.reply_text(
            f"**{name.title()}** cache completely erased.\n\n"
            f"Use `/myc {name}` to generate a fresh card."
        )
    else:
        await message.reply_text(
            f"No cached data found for **{name.title()}**."
        )

