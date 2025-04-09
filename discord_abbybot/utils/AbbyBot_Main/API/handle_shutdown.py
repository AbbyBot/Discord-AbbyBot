import sys
from utils.AbbyBot_Main.API.notify_api_status import notify_api_status

# Signal handler to capture Ctrl+C and notify offline
def handle_shutdown(signal_received, frame):
    print("\033[31m" + "\nBot is shutting down..." + "\033[0m")

    # Notify the API that the bot is offline
    notify_api_status("offline")

    # Close the bot in a controlled manner
    sys.exit(0)