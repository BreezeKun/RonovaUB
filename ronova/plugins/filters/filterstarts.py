from pyrogram import Client, filters
from pyrogram.types import Message

from .errors import NoData

def starts(prefix: str | None = None):
    if prefix is None:
        raise NoData("pass a prefix in starts(prefix:str = '')")

    async def func(flt, c: Client, m: Message):
        if not m.text:
            return False
        return m.text.startswith(prefix)

    return filters.create(func, name="StartsFilter")