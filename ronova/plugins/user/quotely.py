from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import PREFIXES, ADMIN_ID
from ..shared import QUOTE_STATE
from ..decorators import get_string

QUOTLY_BOT: str = "QuotLyBot"

QUOTE_COMMAND:list[str] = ["q"]

def quote_state(
        status:bool = False, 
        user_chat_id:int | None = None, 
        user_message_id: int | None = None
        ) -> None:
    QUOTE_STATE.status = status
    QUOTE_STATE.user_chat_id = user_chat_id
    QUOTE_STATE.user_message_id = user_message_id

@Client.on_message(filters.user(QUOTLY_BOT) & filters.sticker & filters.bot, group= 0)
async def get_quote(c:Client, m:Message):
    if  QUOTE_STATE.status and m.sticker:
        await c.send_sticker(
            chat_id = QUOTE_STATE.user_chat_id, 
            sticker = m.sticker.file_id, 
            reply_parameters= ReplyParameters(message_id = QUOTE_STATE.user_message_id)
            )
        quote_state()
        

@Client.on_message(filters.command(QUOTE_COMMAND, prefixes=PREFIXES) & filters.user(ADMIN_ID), group= 2)
@get_string("quote")
async def quote(c:Client, m:Message):
    """
    Get quotes of your message or replied message
    Usage: q [message] or reply to message with q
    """
    
    rm = m.reply_to_message
    command = m.command[0]

    if command == "q":
        if rm:
            await c.forward_messages(QUOTLY_BOT, m.chat.id, rm.id)
            quote_state(status=True, user_chat_id = m.chat.id, user_message_id = m.id)
        elif len(m.command) > 1:
            await c.send_message(QUOTLY_BOT, " ".join(m.command[1:]))
            quote_state(status=True, user_chat_id = m.chat.id, user_message_id = m.id)
        else:
            await m.edit("usage: q <text> or q with replying to a message")