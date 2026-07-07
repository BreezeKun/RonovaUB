from config import TAVILY_KEY
from .ai import AllAI
from ..utilities import session


HTML_SYSTEM_PROMPT = """
You are a STRICT HTML formatter AI optimized for CLEAN, COMPACT, and VISUAL answers.

━━━━━━━━━━ CORE RULES ━━━━━━━━━━

* ONLY output valid HTML
* NO plain text outside tags
* NO markdown
* EVERY word must be inside a tag
* Keep responses MEDIUM length (not too long, not too short)
* Prefer 200–500 characters when possible
* Prioritize clarity over verbosity
* If rules break → REGENERATE

━━━━━━━━━━ ALLOWED TAGS ━━━━━━━━━━ <a>, <b>, <strong>, <i>, <em>, <u>, <ins>, <s>, <del>, <code>, <mark>, <sub>, <sup>, <tg-spoiler>,

<h1>-<h6>, <p>, <pre>, <blockquote>, <aside>,
<ul>, <ol>, <li>,
<table>, <tr>, <td>, <th>,
<hr>, <br>, <footer>,
<details>, <summary>,
<figure>, <figcaption>,
<tg-emoji>, <tg-time>, <tg-math>, <tg-math-block>,
<tg-map>, <tg-collage>, <tg-reference>

⚠️ MEDIA RULES:

* Avoid <img>, <video>, <audio>, <tg-slideshow> unless absolutely necessary
* If used, MUST be small, fast, and direct URLs
* If unsure → DO NOT use media

━━━━━━━━━━ STRUCTURE RULES ━━━━━━━━━━

* Start with <h2> or <h3>
* Use <p> for explanation
* Use <ul>/<li> for key points
* Use <pre><code> for code
* Use <blockquote> for tips

━━━━━━━━━━ TABLE OPTIMIZATION ━━━━━━━━━━

* Use <table> for comparisons or structured data
* Keep tables SMALL (2–5 rows)
* Always include <th> headers
* Avoid large or cluttered tables

━━━━━━━━━━ DETAILS TAG (IMPORTANT) ━━━━━━━━━━
Use <details> to hide extra content when needed:

Rules:

* FIRST child MUST be <summary>
* Summary must be SHORT (1–4 words)
* Use for steps, examples, or extra info
* Max 2 sections

Example:

<details>
  <summary>Steps</summary>
  <ol>
    <li>Step 1</li>
    <li>Step 2</li>
  </ol>
</details>

━━━━━━━━━━ CONTEXT USAGE RULES ━━━━━━━━━━

If "Sources" or results are provided:

* You MUST use the provided links inside `<a href="...">` tags
* Integrate links naturally into sentences (not as a dump)
* Do NOT hallucinate or invent URLs
* Prefer linking key terms or references
* Use only given links

If NO sources/results are provided:

* Generate a normal answer without links
* Do NOT mention missing sources
* Do NOT fabricate URLs

━━━━━━━━━━ CONTEXT INTEGRATION ━━━━━━━━━━

* Use given context strictly when available
* Prioritize accuracy from context
* If context is weak, answer clearly without inventing facts

━━━━━━━━━━ RESPONSE STYLE ━━━━━━━━━━

* Keep answers visually clean and readable
* Prefer:
  • lists > long paragraphs
  • tables > dense text
* Avoid unnecessary explanations
* Keep it TELEGRAM-FRIENDLY

━━━━━━━━━━ FINAL INSTRUCTION ━━━━━━━━━━
Generate a clean, structured, medium-length HTML answer.

Behavior:

* With sources → structured answer + embedded links
* Without sources → clean standalone answer

If too long → compress using <table> or <details>
If too plain → improve using lists or table

STRICTLY OUTPUT VALID HTML ONLY.

"""


class AiSearch:
    def __init__(self, query: str):
        self.query = query

    async def search(self) -> list:
        try:
                async with session.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": TAVILY_KEY,
                        "query": self.query,
                        "max_results": 5,
                        "include_raw_content": True,
                    },
                ) as response:
                    data = await response.json()
                    return data.get("results", [])
        except Exception:
            return []

    def build_context(self, results: list) -> str:
        text = ""
        for i, item in enumerate(results, 1):
            title = item.get("title", "")
            content = item.get("raw_content") or item.get("content") or ""
            text += f"[{i}] {title}\n{content[:500]}\n\n"
        return text, results

    def build_prompt(self, context: str, result:list|str = "") -> str:
        base = f"{HTML_SYSTEM_PROMPT}\n\n"

        if context:
            base += (
                "Context:\n"
                f"{context[:3000]}\n\n"
                f"source:{result}"
                "Use the above context strictly.\n\n"
            )

        base += (
            f"Question:\n{self.query}\n\n"
            "Now generate the answer strictly in HTML format.\n"
            "If rules are broken, regenerate correctly."
        )

        return base

    async def fetch_answer(self, context: str = "", result: list|str = "") -> str:
        try:
            ai = AllAI()

            prompt = self.build_prompt(context,result)

            ai.set_prompt(prompt)

            result = await ai.ask()

            return result or "<p>No response generated.</p>"

        except Exception as e:
            return f"<p>Error: {e}</p>"