import os

from dotenv import load_dotenv


load_dotenv()


API_ID: int = int(os.getenv('api_id'))
API_HASH: str = os.getenv('api_hash')
BOT_TOKEN: str = os.getenv('bot_token')
BOT:str = os.getenv('bot')
ADMIN_ID: list[int] = [int(os.getenv('admin'))]
SESSION_STRING: str = os.getenv('string_session')
TAVILY_KEY: str = os.getenv('tavily_key')
TMDB_KEY:str = os.getenv('tmdb_key')
GEMINI_KEY:str = os.getenv('gemini_key')
GROQ_KEY:str = os.getenv('groq_key')
RENDER_API:str = os.getenv('render_api')
POSTGRE_KEY:str = os.getenv('postgre_con_str')

PREFIXES: list[str] = [".", "@", "#", "$", "%", "^", "&", "*", "~", ""]