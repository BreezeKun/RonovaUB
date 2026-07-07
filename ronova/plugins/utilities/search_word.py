from ..utilities import session

async def word_search(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    async with session.get(url) as resp:
            data = await resp.json()

            if not isinstance(data, list):
                return {"error": "Word not found"}

            base = data[0]

            result = {
                "word": base.get("word"),
                "phonetic": base.get("phonetic"),
                "audio": None,
                "origin": base.get("origin"),
                "meanings": [],
                "source": base.get("sourceUrls", [])
            }

            for p in base.get("phonetics", []):
                if p.get("audio"):
                    result["audio"] = p["audio"]
                    break

            for meaning in base.get("meanings", []):
                m = {
                    "part_of_speech": meaning.get("partOfSpeech"),
                    "definitions": [],
                    "synonyms": meaning.get("synonyms", [])[:5],
                    "antonyms": meaning.get("antonyms", [])[:5],
                }

                for d in meaning.get("definitions", [])[:3]:
                    m["definitions"].append({
                        "definition": d.get("definition"),
                        "example": d.get("example")
                    })

                result["meanings"].append(m)

            return result