from pydantic import BaseModel

DROP_COOLDOWN_SECONDS = 120
WORK_COOLDOWN_SECONDS = 3_600
DAILY_COOLDOWN_SECONDS = 24 * 3_600

class Cooldown(BaseModel):
    work: int = 0
    drop: int = 0
    daily: int = 0
