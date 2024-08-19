from pydantic import BaseModel


class Profile(BaseModel):
    user_id: int
    favorite: str = "none"
    bio: str = ""
