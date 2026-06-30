import aiohttp

async def wiki_search(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"

    headers = {
        "User-Agent": "MyTelegramBot/1.0 (https://example.com; your@email.com)"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            data = await resp.json()
            title = data['title']

            thumbnail = data['originalimage']['source']

            description = data['description']

            source_url = data['content_urls']['desktop']['page']

            summary = data['extract']

            return (title, thumbnail, description, source_url, summary)



