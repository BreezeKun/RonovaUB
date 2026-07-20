import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, ADMIN_ID
from .utils import RetriveData

COMMAND_BANS: list[str] = ["kick", "dkick", "ckick", "skick"]


async def kick_user(
    c: Client,
    m: Message,
    chat_id: int,
    target_id: int,
    revoke_messages: bool = False,
    revoke_reactions: bool = False,
):
    try:
        await c.ban_chat_member(
            chat_id=chat_id,
            user_id=target_id,
            revoke_messages=revoke_messages,
            revoke_reactions=revoke_reactions,
        )
        await asyncio.sleep(1)
        await c.unban_chat_member(
            chat_id=chat_id,
            user_id=target_id
            )
        return True

    except Exception as e:
        await m.reply_text(f"kick failed:\n{e}")
        return False


@Client.on_message(
    filters.command(COMMAND_BANS, prefixes=PREFIXES)
    & filters.user(ADMIN_ID)
    & filters.group
)
async def gc_mang(c: Client, m: Message):

    parser = RetriveData(c, m)
    data = await parser.ban_data()

    chat_id = data["chat_id"]
    target_id = data["target_id"]
    reason = data["reason"]

    if not target_id:
        return await m.reply_text("No target user found.")

    if target_id == m.from_user.id:
        return await m.reply_text("You can't kick yourself.")

    cmd = m.command[0]

    try:
        user = await c.get_users(target_id)
        name = user.first_name
        mention = f"[{name}](tg://user?id={target_id})"
    except:
        mention = f"`{target_id}`"

    text = f"kicked {mention}"
    if reason:
        text += f"\nReason: {reason}"

    if cmd == "kick":
        if await kick_user(c, m, chat_id, target_id):
            await m.reply_text(text)

    elif cmd == "dkick":
        if m.reply_to_message:
            try:
                await m.reply_to_message.delete()
            except:
                pass

        if await kick_user(c, m, chat_id, target_id):
            await m.reply_text(text)

    elif cmd == "skick":
        success = await kick_user(c, m, chat_id, target_id)
        try:
            await m.delete()
        except:
            pass

    elif cmd == "ckick":
        if await kick_user(
            c,
            m,
            chat_id,
            target_id,
            revoke_messages=True,
            revoke_reactions=True,
        ):
            await m.reply_text(text)