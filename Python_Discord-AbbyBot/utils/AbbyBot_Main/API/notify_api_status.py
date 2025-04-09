import os
import requests

def notify_api_status(status):
    try:
        # API URL
        api_url = os.getenv("API_URL")
        if not api_url:
            print("\033[31mAPI URL not found. Check your environment variables.\033[0m")
            return

        # Data to be sent to the API
        data = {"status": status}

        # POST request to the API with the data in JSON format
        response = requests.post(api_url, json=data)

        # Check the API response code
        if response.status_code == 200:

            print("\033[32m" + f"API notified: AbbyBot is {status}." + "\033[0m")
        else:

            print("\033[33m" + f"Failed to notify API. Status code: {response.status_code}, Response: {response.text}" + "\033[0m")
    except requests.exceptions.RequestException as e:

        print("\033[31m" + f"Error notifying API: {e}" + "\033[0m")

def update_bot_info(bot):
    try:
        api_url = os.getenv("API_URL")

        if not api_url:
            print("\033[31mAPI URL not found. Check your environment variables.\033[0m")
            return
        
        bot_id = bot.user.id

        bot_avatar = bot.user.avatar

        bot_name = bot.user.name

        # Work in progress

        print(f"bot: info {bot_id} {bot_name} {bot_avatar}")

        
    except requests.exceptions.RequestException as e:

        print("\033[31m" + f"Error updating bot info: {e}" + "\033[0m")