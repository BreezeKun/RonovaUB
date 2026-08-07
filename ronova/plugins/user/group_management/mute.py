from datetime import datetime, timezone
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

from config import PREFIXES, ADMIN_ID
from .utils import RetriveData, format_duration
from ...decorators import get_string


COMMAND_BANS: list[str] = ["mute", "dmute", "smute"]

async def mute_user(
    c: Client,
    m: Message,
    chat_id: int,
    target_id: int,
    time: Optional[datetime]
):
    try:
        await c.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_id,
            until_date=time,
            permissions=ChatPermissions(
                can_send_messages = False,
                can_send_audios = False,
                can_send_documents = False,
                can_send_photos = False,
                can_send_videos = False,
                can_send_video_notes = False,
                can_send_voice_notes = False,
                can_send_polls = False,
                can_send_other_messages = False,
                can_add_web_page_previews = False,
                can_react_to_messages = False,
                can_edit_tag = False,
                can_change_info = False,
                can_invite_users = False,
                can_pin_messages = False,
                can_manage_topics = False)
        )
        return True
    
    except Exception as e:
        await m.reply_text(f"Mute failed:\n{e}")
        return False

@Client.on_message(
    filters.command(COMMAND_BANS, prefixes=PREFIXES)
    & filters.user(ADMIN_ID)
    & filters.group
)
@get_string("mute")
async def gc_mang_mute(c: Client, m: Message):
    """
    Mute a user
    Usage: mute [user name/id] or reply [time/optional] [reason/optional]
    types:
    mute - mutes a user
    smute - silently mutes a user
    dmute - mutes user and deletes replied message
    """

    parser = RetriveData(c, m)
    data = await parser.ban_data()

    chat_id = data["chat_id"]
    target_id = data["target_id"]
    time = data["time"]
    reason = data["reason"]

    if not target_id:
        return await m.reply_text("No target user found.")

    if target_id == m.from_user.id:
        return await m.reply_text("You can't mute yourself.")

    cmd = m.command[0]
    duration = format_duration(time)

    try:
        user = await c.get_users(target_id)
        name = user.first_name
        mention = f"[{name}](tg://user?id={target_id})"
    except:
        mention = f"`{target_id}`"

    text = f"muted {mention} for {duration}"
    if reason:
        text += f"\nReason: {reason}"

    if cmd == "mute":
        if await mute_user(c, m, chat_id, target_id, time):
            await m.reply_text(text)

    elif cmd == "dmute":
        if m.reply_to_message:
            try:
                await m.reply_to_message.delete()
            except:
                pass

        if await mute_user(c, m, chat_id, target_id, time):
            await m.reply_text(text)

    elif cmd == "smute":
        success = await mute_user(c, m, chat_id, target_id, time)
        try:
            await m.delete()
        except:
            pass