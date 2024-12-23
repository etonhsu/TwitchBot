import os
import json
import requests
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv

TOKEN_FILE = "api_token.json"

# Load environment variables from .env file
load_dotenv()

def get_app_access_token(client_id, client_secret):
    """
    Requests a new access token using the Client Credentials flow.
    """
    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        token_data["expires_at"] = (datetime.now(UTC) + timedelta(seconds=token_data["expires_in"])).isoformat()
        save_token(token_data)
        return token_data["access_token"]
    else:
        raise Exception(f"Failed to get token: {response.status_code}, {response.text}")

def save_token(token_data):
    """
    Saves the token data to a local file.
    """
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)

def load_token():
    """
    Loads the token data from a local file if it exists.
    """
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def is_token_valid(token_data):
    """
    Checks if the token is still valid based on the expiration time.
    """
    if not token_data or "expires_at" not in token_data:
        return False
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    return datetime.now(UTC) < expires_at

def get_valid_access_token(client_id, client_secret):
    """
    Returns a valid access token, refreshing it if necessary.
    """
    token_data = load_token()
    if token_data and is_token_valid(token_data):
        return token_data["access_token"]
    else:
        return get_app_access_token(client_id, client_secret)

def make_twitch_request(client_id, client_secret, endpoint, params=None):
    """
    Makes a request to the Twitch API, automatically handling token generation and refresh.
    """
    access_token = get_valid_access_token(client_id, client_secret)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': client_id
    }
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed: {response.status_code}, {response.text}")
