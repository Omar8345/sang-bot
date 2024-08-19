from pydantic import BaseModel



class GachaHistory(BaseModel):
    user_id: int
    time: int = 0
    rewards: str


class GachaInfo(BaseModel):
    user_id: int
    pity: int = 60
    chance_increase: int = 0
    selected_card: str = "none"
    gacha_history: list[GachaHistory]
