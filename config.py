import os

from dotenv import load_dotenv


load_dotenv()


API_ID_C1: int = int(os.getenv('api_id_1','0'))
API_HASH_C1: str = os.getenv('api_hash_1','')
SESSION_STRING_C1: str = os.getenv('string_session_1','')
API_ID_C2: int = int(os.getenv('api_id_2','0'))
API_HASH_C2: str = os.getenv('api_hash_2','')
SESSION_STRING_C2: str = os.getenv('string_session_2','')
BOT_TOKEN: str = os.getenv('bot_token','')
BOT:str = os.getenv('bot','')
ADMIN_ID: list[int | str] = [int(os.getenv('admin','[0]'))]
TAVILY_KEY: str = os.getenv('tavily_key','')
TMDB_KEY:str = os.getenv('tmdb_key','')
GEMINI_KEY:str = os.getenv('gemini_key','')
GROQ_KEY:str = os.getenv('groq_key','')
POSTGRE_KEY:str = os.getenv('postgre_con_str','')
GI_UID:int = int((os.getenv('gi_uid','0')))



PREFIXES: list[str] = [".", "@", "#", "$", "%", "^", "&", "*", "~", ""]

__all__:list[str] = [
    "API_ID_C1", "API_HASH_C1", "BOT_TOKEN",
    "API_ID_C2", "API_HASH_C2","SESSION_STRING_C2",
    "BOT", "ADMIN_ID", "SESSION_STRING_C1",
    "TAVILY_KEY", "TMDB_KEY", "GEMINI_KEY",
    "GROQ_KEY", "POSTGRE_KEY"]