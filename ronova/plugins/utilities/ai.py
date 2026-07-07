import random
from google import genai
from openai import OpenAI

from config import GEMINI_KEY, GROQ_KEY
from ..utilities import session


class AllAI:
    def __init__(self):
        self.query = ""
        self.gemini_client = genai.Client(api_key=GEMINI_KEY)
        self.groq_client = OpenAI(
            api_key=GROQ_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

        self.groq_models = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-20b"
        ]

    def set_prompt(self, text: str):
        self.query = text

    async def gemini(self):
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-3.5-flash",
                contents=self.query
            )
            return response.text

        except Exception as e:
            return f"[Gemini Error] {e}"

    async def groq(self):
        try:
            model = random.choice(self.groq_models)

            response = self.groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": self.query}],
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"[Groq Error] {e}"

    async def binjie(self, context: str = ""):
        try:
            prompt = context or self.query

            payload = {
                "prompt": prompt,
                "network": True,
                "stream": False,
                "system": {
                    "userId": "#/chat/1722576084617",
                    "withoutContext": not bool(context),
                },
            }
            async with session.post(
                    "https://api.binjie.fun/api/generateStream",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                ) as response:
                    return await response.text()

        except Exception as e:
            return f"[Binjie Error] {e}"

    async def ask(self):
        func = random.choice([self.gemini, self.groq, self.binjie])

        result = await func()

        return result or "AI failed."