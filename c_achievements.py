from pydantic import BaseModel


class Achievement(BaseModel):
    user_id: int
    name: str
    progress: int
    collected: int


class Achievements(BaseModel):
    user_id: int
    achievements: list[Achievement] = []
    cards_collected: int = 0
