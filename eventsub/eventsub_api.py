import requests
import os
from dotenv import load_dotenv
from auth.api_auth import get_app_access_token

# Load environment variables from .env file
load_dotenv()

client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")
webhook_secret = os.getenv("TWITCH_WEBHOOK_SECRET")
callback_url = "https://fe42-174-160-52-35.ngrok-free.app"

def fetch_eventsub(access_token):
    url = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": client_id
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        raise Exception(f"Failed to fetch EventSub subscriptions: {response.status_code}, {response.text}")


def sub_eventsub(access_token, event_type, condition):
    url = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": client_id,
        "Content-Type": "application/json"
    }
    payload = {
        "type": event_type,
        "version": "1",
        "condition": condition,
        "transport": {
            "method": "webhook",
            "callback": callback_url,
            "secret": webhook_secret
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 202:
        print(f"Subscribed to {event_type}")
    else:
        raise Exception(f"Failed to subscribe to {event_type}: {response.status_code}, {response.text}")


def verify_eventsub(streamer_id):
    """
    Ensure the correct EventSub subscriptions for the specified streamer.
    """
    access_token = get_app_access_token(client_id, client_secret)

    # Required EventSub topics for the streamer
    required_subscriptions = [
        {"type": "stream.online", "condition": {"broadcaster_user_id": streamer_id}},
        {"type": "channel.subscribe", "condition": {"broadcaster_user_id": streamer_id}},
        {"type": "channel.follow", "condition": {"broadcaster_user_id": streamer_id}},
    ]

    # Fetch existing subscriptions
    existing_subscriptions = fetch_eventsub(access_token)

    # Extract active subscription types and conditions
    existing_conditions = [
        {"type": sub["type"], "condition": sub["condition"]}
        for sub in existing_subscriptions
    ]

    # Check and subscribe to missing topics
    for required in required_subscriptions:
        if required not in existing_conditions:
            sub_eventsub(access_token, required["type"], required["condition"])
        else:
            print(f"Already subscribed to {required['type']} for {streamer_id}")