from datetime import datetime, timezone
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, ADMIN_ID
from .utils import RetriveData, format_duration
from ...decorators import get_string

COMMAND_BANS: list[str] = ["ban", "dban", "cban", "sban"]


async def ban_user(
    c: Client,
    m: Message,
    chat_id: int,
    target_id: int,
    time: Optional[datetime],
    revoke_messages: bool = False,
    revoke_reactions: bool = False,
):
    try:
        await c.ban_chat_member(
            chat_id=chat_id,
            user_id=target_id,
            until_date=time,
            revoke_messages=revoke_messages,
            revoke_reactions=revoke_reactions,
        )
        return True

    except Exception as e:
        await m.reply_text(f"Ban failed:\n{e}")
        return False


@Client.on_message(
    filters.command(COMMAND_BANS, prefixes=PREFIXES)
    & filters.user(ADMIN_ID)
    & filters.group
)
@get_string("ban")
async def gc_mang(c: Client, m: Message):
    """
    Ban a specefic user
    Usage: ban [user name/id] or reply [time/optional] [reason/optional]

    types:
    ban - bans a user
    dban - deletes replied message and bans user
    cban - bans user and revoke his reaction, messages
    sban - silently bans a user
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
        return await m.reply_text("You can't ban yourself.")

    cmd = m.command[0]
    duration = format_duration(time)

    try:
        user = await c.get_users(target_id)
        name = user.first_name
        mention = f"[{name}](tg://user?id={target_id})"
    except:
        mention = f"`{target_id}`"

    text = f"Banned {mention} for {duration}"
    if reason:
        text += f"\nReason: {reason}"

    if cmd == "ban":
        if await ban_user(c, m, chat_id, target_id, time):
            await m.reply_text(text)

    elif cmd == "dban":
        if m.reply_to_message:
            try:
                await m.reply_to_message.delete()
            except:
                pass

        if await ban_user(c, m, chat_id, target_id, time):
            await m.reply_text(text)

    elif cmd == "sban":
        success = await ban_user(c, m, chat_id, target_id, time)
        try:
            await m.delete()
        except:
            pass

    elif cmd == "cban":
        if await ban_user(
            c,
            m,
            chat_id,
            target_id,
            time,
            revoke_messages=True,
            revoke_reactions=True,
        ):
            await m.reply_text(text)