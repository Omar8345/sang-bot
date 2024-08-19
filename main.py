import bot
import settings
from dotenv import load_dotenv
import os


# loads the token
load_dotenv()

settings.init()

bot.run(token = os.environ["TOKEN"])
