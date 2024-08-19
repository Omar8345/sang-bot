import prisma
from pydantic import BaseModel
from c_card import SoldCard

class Shop(BaseModel):
    cards: list[SoldCard]
    user_id: int
    bio: str = ""
    image: str = "none"
