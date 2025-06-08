from ABH import ABH, events, bot_token
from datetime import datetime
import os, json, pytz
from code import *)
def main():
    print("config is starting...")
    ABH.start(bot_token=bot_token)
    ABH.run_until_disconnected()
if __name__ == "__main__":
    main()
