import discord
from error_handling import retry_on_error, log_error
import os
import importlib
from command_handler import commands
import time

bot = discord.Client(intents=discord.Intents.all())

events = {}

# please only use / :3
# also keep it simple(it will also be used with importlib, and it doesn't like most paths)
COMMANDS_DIRECTORY = "slash_commands"
EVENTS_DIRECTORY = "events"
ADMIN_COMMANDS_DIRECTORY = "admin/slash_commands"
ADMIN_EVENTS_DIRECTORY = "admin/events"


tree = discord.app_commands.CommandTree(bot)

def load_commands(path: str) -> None:
    """
    Meant to load commands for the first time, don't use it as a way to reload commands.
    :return: None
    """
    for command in os.listdir(path):
        if command.endswith("py"):
            try:
                command_name = command[:-3]

                command_handler = importlib.import_module(f"{path.replace('/', '.').rstrip('.')}.{command[:-3]}")
                # commands[command_name] = command_handler
            except Exception as e:
                log_error(e)
                raise KeyboardInterrupt("issue loading commands") # KeyboardInterrupt is the only exception that doesn't get caught


def load_events(path: str) -> None:
    """
    Meant to load events for the first time, don't use it as a way to reload events.
    :return: None
    """
    for event in os.listdir(path):
        if event.endswith("py"):
            try:
                event_name = event[:-3]


                event_handler = importlib.import_module(f"{path.replace('/', '.').rstrip('.')}.{event_name}").handle
                # events[event_name] = event_handler

                event_handler.__name__ = event_name
                bot.event(event_handler)
            except Exception as e:
                log_error(e)
                raise KeyboardInterrupt("issue loading events") # KeyboardInterrupt is the only exception that doesn't get caught


@retry_on_error(log=True)
def run(token: str, admin: bool = False) -> None:
    try:
        commands_path = COMMANDS_DIRECTORY
        events_path = EVENTS_DIRECTORY
        if admin:
            commands_path = ADMIN_COMMANDS_DIRECTORY
            events_path = ADMIN_EVENTS_DIRECTORY

        load_commands(commands_path)
        load_events(events_path)
    except Exception as e:
        log_error(e)
        exit(-1)

    while True:
        try:
            bot.run(token=token)
        except Exception as e:
            log_error(e)
            print("THRES AN ISSUE WITH THE BOT")
            print("retrying in 20 seconds")

        time.sleep(20)
