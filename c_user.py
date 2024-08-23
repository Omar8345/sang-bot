from pydantic import BaseModel
from c_card import Card
from c_profile import Profile
from c_folder import Folder
from c_gacha import GachaInfo
from c_achievements import Achievements


class User(BaseModel):
    balance: int = 0
    user_id: int
    cards: list[Card]
    profile: Profile
    buds: int = 0
    folders: list[Folder]
    gacha_info: GachaInfo
    achievements: Achievements = None
