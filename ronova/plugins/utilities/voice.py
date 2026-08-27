import asyncio
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pytgcalls import filters

from ronova import ub
from .get_music import MUSIC_PLAYER


class VoiceChatPlayer:

    def __init__(self):
        self.call = PyTgCalls(ub)

        self.chat_id = None
        self.current = None
        self.playing = False

        self.lock = asyncio.Lock()

    async def start(self):
        await self.call.start()

    async def join(self, chat_id: int):
        self.chat_id = chat_id

    async def play_next(self):

        async with self.lock:

            if self.playing:
                return

            music = MUSIC_PLAYER.get_next()

            if not music:
                self.playing = False
                self.current = None
                return

            self.current = music
            self.playing = True

            print(
                f"Playing: "
                f"{music['title']} - "
                f"{music['artist']}"
            )

            await self.call.play(
                self.chat_id,
                MediaStream(music["filename"])
            )

    async def stop(self):

        if self.chat_id:
            try:
                await self.call.leave_call(self.chat_id)
            except Exception:
                pass

        self.playing = False
        self.current = None
        self.chat_id = None

    async def next(self):

        if self.chat_id:
            try:
                await self.call.leave_call(self.chat_id)
            except Exception:
                pass

        self.playing = False
        self.current = None

        await self.play_next()


VOICE_PLAYER = VoiceChatPlayer()