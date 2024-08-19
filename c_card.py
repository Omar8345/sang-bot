from pydantic import BaseModel


class Card(BaseModel):
    amount: int = 0
    card_id: str
    user_id: int

class SoldCard(BaseModel):
    amount: int = 0
    price: int = 0
    item_id: int = 0
    card_id: str
    user_id: int

class NewSoldCard(BaseModel):
    amount: int = 0
    price: int = 0
    card_id: str
    user_id: int