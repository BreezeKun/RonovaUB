from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, ADMIN_ID
from ..database import sudo_methods
from ..utilities import get_target_id

SUDO_COMMANDS: list[str] = ["addsudo", "remsudo", "listsudo"]

@Client.on_message(filters.command(SUDO_COMMANDS, prefixes=PREFIXES) & filters.user(ADMIN_ID))
async def sudo_handler(c: Client, m: Message):
    command = m.command[0]

    if command in ["addsudo", "remsudo"]:
        TARGET = await get_target_id(c, m)

        if not TARGET:
            return await m.reply_text("Failed to get user")

        if command == "addsudo":
            sudo_methods.add_sudo(TARGET)
            await m.reply_text(f"Added `{TARGET}` as sudo")
        else:
            sudo_methods.rem_sudo(TARGET)
            await m.reply_text(f"Removed `{TARGET}` from sudo")

    elif command == "listsudo":
        users = sudo_methods.get_sudo()

        if not users:
            return await m.reply_text("No sudo users found")

        text = "**Sudo Users:**\n\n" + "\n".join(f"- `{u}`" for u in users)
        await m.reply_text(text)