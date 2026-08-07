from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, ADMIN_ID
from .utils import RetriveData
from ...decorators import get_string

COMMAND_UNBANS: list[str] = ["unban"]

@Client.on_message(
    filters.command(COMMAND_UNBANS, prefixes=PREFIXES)
    & filters.user(ADMIN_ID)
    & filters.group
)
@get_string("unban")
async def gc_mang_unban(c: Client, m: Message):
    """
    To unban a user
    Usage: unban [user name/id] or reply
    """

    parser = RetriveData(c, m)
    data = await parser.unban_data()

    chat_id = data["chat_id"]
    target_id = data["target_id"]

    if not target_id or target_id == m.from_user.id:
        return

    try:
        await c.unban_chat_member(chat_id=chat_id, user_id=target_id)
        await m.reply_text(f"Unbanned user `{target_id}`")
    except Exception as e:
        await m.edit(e)