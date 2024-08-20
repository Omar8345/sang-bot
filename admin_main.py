import bot
import settings
from dotenv import load_dotenv
import os
import subprocess

# loads the token
load_dotenv()

settings.init()

bot.run(token = os.environ["ADMIN_TOKEN"], admin = True)
