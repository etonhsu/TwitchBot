from auth.api_auth import get_valid_access_token
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def check_viewership(client_id, client_secret, streamer_username):
    # Get access token
    access_token = get_valid_access_token(client_id, client_secret)

    # Set up request
    endpoint = 'https://api.twitch.tv/helix/streams'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': client_id
    }
    params = {'user_login': streamer_username}

    # Make API call
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            stream_info = data['data'][0]  # Stream data for the user
            viewer_count = stream_info['viewer_count']
            print(f"{streamer_username} has {viewer_count} viewers.")
        else:
            print(f"{streamer_username} is not currently live.")
    else:
        raise Exception(f"API request failed: {response.status_code}, {response.text}")

# Environment variables
client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")

# Example usage
streamer_username = ('k3soju')
try:
    check_viewership(client_id, client_secret, streamer_username)
except Exception as e:
    print(f"Error: {e}")
