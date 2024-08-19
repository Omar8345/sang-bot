from pydantic import BaseModel


class Cooldown(BaseModel):
    work: int = 0
    drop: int = 0
    daily: int = 0
