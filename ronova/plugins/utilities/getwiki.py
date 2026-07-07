from ..utilities import session

async def wiki_search(query: str):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"

    async with session.get(url) as resp:
            if resp.status == 404:
                return None

            data = await resp.json()

            title = data.get("title", query)
            thumbnail = data.get("originalimage", {}).get("source", "")
            description = data.get("description", "")
            source_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
            summary = data.get("extract", "")

            return title, thumbnail, description, source_url, summary