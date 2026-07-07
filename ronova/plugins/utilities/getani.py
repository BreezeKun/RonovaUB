from ..utilities import session

url = "https://graphql.anilist.co"

query = """
query ($search: String) {
  Media(search: $search, type: ANIME) {
    id
    title {
      english
      native
    }
    description(asHtml: false)
    status
    episodes
    averageScore
    genres
  }
}
"""

async def fetch_anime(name):
        async with session.post(url, json={
            "query": query,
            "variables": {"search": name}
        }) as res:
            data        = await res.json()
            anime_data  = data['data']['Media']

            anime_id    = anime_data['id']
            status      = anime_data['status']
            episodes    = anime_data['episodes']
            score       = anime_data['averageScore']
            genres      = anime_data['genres']
            description = anime_data['description']
            en_name     = anime_data['title']['english']
            native_name = anime_data['title']['native']

            return (anime_id, status, episodes, score, genres, description, en_name, native_name)