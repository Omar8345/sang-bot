from pydantic import BaseModel


class Folder(BaseModel):
    user_id: int
    name: str
    cards: list[str]
