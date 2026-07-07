from ..utilities import session

class PasteRS:
    BASE = "https://paste.rs"

    async def create(self, content):
            async with session.post(self.BASE, data=content) as r:
                return await r.text()
    async def delete(self, paste_id):
            async with session.delete(f"{self.BASE}/{paste_id}") as r:
                return r.status

paste = PasteRS()