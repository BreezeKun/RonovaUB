import os
import json
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from enkard.enka import GenshinClient, gi
from enkard.enkacard.encbanner import CreateBanner
from enkard.enkacard.utils.create_banner_one import generationOne

from config import ADMIN_ID, PREFIXES


UID = 1817389136
DOWNLOAD_DIR = "gidownloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def generate_character_card(name: str) -> str | None:
    """
    Generate a character card and return its file path.
    """

    async with GenshinClient(gi.Language.ENGLISH) as client:
        response = await client.fetch_showcase(UID)
        data = response.model_dump()

    response_data = CreateBanner(data=data, custom_image={"Skirk":"https://ik.imagekit.io/cocogoat/1352449904-10000114_WWvIz_L1L"}).generate()

    # Find the character case-insensitively
    character_data = None
    actual_name = None

    for char_name, char_data in response_data.items():
        if char_name.lower() == name.lower():
            character_data = char_data
            actual_name = char_name
            break

    if character_data is None:
        return None

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{actual_name.lower()}.png"
    )

    banner = await generationOne(
        character_data,
        adapt=False,
        lvl="Level",
        uid=str(UID),
        hide_uid=False,
    )

    banner.save(file_path)

    return file_path


@Client.on_message(filters.command("myc", prefixes=PREFIXES) & filters.user(ADMIN_ID))
async def myc_command(client: Client, message: Message):

    # /myc odette
    if len(message.command) < 2:
        await message.reply_text(
            "Usage:\n/myc <character>\n\n"
            "Example:\n/myc odette"
        )
        return

    name = " ".join(message.command[1:]).strip()

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{name.lower()}.png"
    )

    # Already generated
    if os.path.exists(file_path):
        await message.reply_photo(
            photo=file_path,
            caption=f"{name.title()}"
        )
        return

    # Generate
    status = await message.reply_text(
        f"Generating **{name.title()}**..."
    )

    try:
        file_path = await generate_character_card(name)

        if file_path is None:
            await status.edit_text(
                f"Character **{name.title()}** was not found "
                "in the showcase."
            )
            return

        await status.delete()

        await message.reply_photo(
            photo=file_path,
            caption=f"{name.title()}"
        )

    except Exception as e:
        await status.edit_text(
            f"Failed to generate the card.\n\n"
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

    for extension in (".jpg", ".png"):
        file_path = os.path.join(
            DOWNLOAD_DIR,
            f"{name}{extension}"
        )

        if os.path.isfile(file_path):
            os.remove(file_path)
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