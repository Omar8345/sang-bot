import json
from pydantic import BaseModel
from functools import reduce


class Settings(BaseModel):
    status: str = "online"
    prefix: str
    guild_id: int
    embed_color: int
    hehet_emoji: str
    bud_emoji: str
    bud_price: int
    tier_emojis: dict[str, str]


def remove_comments(text: str, comment_symbol: str) -> str:
    return "\n".join([i.split(comment_symbol)[0] for i in text.split('\n')])


def process_color(settings: dict) -> None:
    if not isinstance(settings["embed_color"], str):
        settings["embed_color"] = reduce(lambda a, b: a << 8 | b, settings["embed_color"], 0)
    else:
        settings["embed_color"] = int(settings["embed_color"], 16)


settings: Settings
def init():
    global settings

    with open("settings.json") as f:
        content = f.read()
        no_comments = remove_comments(content, '//')
        loaded_settings = json.loads(no_comments)

    process_color(loaded_settings)

    settings = Settings(**loaded_settings)

