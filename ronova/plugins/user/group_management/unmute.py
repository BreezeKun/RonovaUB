from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

from config import PREFIXES, ADMIN_ID
from .utils import RetriveData
from ...decorators import get_string

COMMAND_UNBANS: list[str] = ["unmute"]

@Client.on_message(
    filters.command(COMMAND_UNBANS, prefixes=PREFIXES)
    & filters.user(ADMIN_ID)
    & filters.group
)
@get_string("unmute")
async def gc_mang_unmute(c: Client, m: Message):
    """
    To unmute a user
    Usage: unmute [user name/id] or reply
    """

    parser = RetriveData(c, m)
    data = await parser.unban_data()

    chat_id = data["chat_id"]
    target_id = data["target_id"]

    if not target_id or target_id == m.from_user.id:
        return

    try:
        await c.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_id,
            permissions=ChatPermissions(
                can_send_messages = True,
                can_send_audios = True,
                can_send_documents = True,
                can_send_photos = True,
                can_send_videos = True,
                can_send_video_notes = True,
                can_send_voice_notes = True,
                can_send_polls = True,
                can_send_other_messages = True,
                can_add_web_page_previews = True,
                can_react_to_messages = True,
                can_edit_tag = True,
                can_change_info = True,
                can_invite_users = True,
                can_pin_messages = True,
                can_manage_topics = True)
        )
        await m.reply_text(f"unmuted user `{target_id}`")
    except Exception as e:
        await m.edit(e)