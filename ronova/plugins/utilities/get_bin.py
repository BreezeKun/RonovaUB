import aiohttp

class PasteRS:
    BASE = "https://paste.rs"

    async def create(self, content):
        async with aiohttp.ClientSession() as s:
            async with s.post(self.BASE, data=content) as r:
                return await r.text()
    async def delete(self, paste_id):
        async with aiohttp.ClientSession() as s:
            async with s.delete(f"{self.BASE}/{paste_id}") as r:
                return r.status

paste = PasteRS()