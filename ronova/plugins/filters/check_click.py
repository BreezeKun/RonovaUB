from pyrogram import Client, filters
from pyrogram.types import Message

from config import BOT_TOKEN

def check():
    '''
    This meathod checks if the message is inline or not and its clickable or not
    created for clicking those message to turn it into premium
    '''

    bot_id = int(BOT_TOKEN.split(":")[0])

    async def func(flt, c: Client, m: Message):
        return True if m.via_bot and m.reply_markup and m.via_bot.id == bot_id  else False
    
    return filters.create(func, name="ClickFilter")