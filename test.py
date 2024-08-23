from pydantic import BaseModel

class Rat(BaseModel):
    size: int = 1_000
    length: int = 1_000

rat = Rat()
print(rat.__getattr__("size"))
