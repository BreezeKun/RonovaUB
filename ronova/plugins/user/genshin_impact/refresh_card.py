import os

from pyrogram import Client, filters
from pyrogram.types import Message

from config import ADMIN_ID, PREFIXES
from ...utilities import pre_matching, fetch_data
from ...decorators import get_string


DOWNLOAD_DIR = "gidownloads"
RESPONSE_FILE = os.path.join(DOWNLOAD_DIR, "response_data.json")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@Client.on_message(
    filters.command("girefresh", prefixes=PREFIXES)
    & filters.user(ADMIN_ID)
)
@get_string("girefresh")
async def girefresh_command(client: Client, message: Message):
    """usage:
    .girefresh [character name]
    refreshes build card
    """
    if len(message.command) < 2:
        return
    
    data = await fetch_data()
    name = pre_matching(" ".join(message.command[1:]).strip().lower(),data)

    deleted = False

    for extension in (".jpg", ".jpeg", ".png"):
        file_path = os.path.join(
            DOWNLOAD_DIR,
            f"{name}{extension}",
        )

        if os.path.isfile(file_path):
            os.remove(file_path)
            deleted = True

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