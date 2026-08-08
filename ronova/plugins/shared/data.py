from dataclasses import dataclass, field

@dataclass
class AfkState:
    status: bool = False
    reason: str | None = None
    afk_time: float | None = None
    file_type: str | None = None
    file_id: str | None = None
    media_from_chat: int | None = None
    message_media_id: int | None = None
    users: list[int] = field(default_factory=list)

AFK_DATA = AfkState()

@dataclass
class MusicState:
    status: bool = False
    user_chat_id:int | None = None
    user_message_id:int | None = None 

MUSIC_STATE = MusicState()

@dataclass
class QuoteState:
    status: bool = False
    user_chat_id:int | None = None
    user_message_id:int | None = None

QUOTE_STATE =  QuoteState()

@dataclass
class PremiumState:
    status: bool = False
    text: str | None = None

PREMIUM_STATE = PremiumState()

@dataclass
class HelpStorage:
    data:dict = field(default_factory=dict)

HELP_STORAGE = HelpStorage()

class XoxData:
    players = {}

    def __init__(self):
        self.data = {}
        self.board = []
        self.status = False

    @classmethod
    def add_game(cls, game_id, game):
        cls.players[game_id] = game

    @classmethod
    def rem_game(cls, game_id):
        cls.players.pop(game_id)