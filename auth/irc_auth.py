import requests
import json
import os
import requests

IRC_TOKEN_FILE = os.path.join("tokens", "irc_token.json")

def load_tokens(filename=IRC_TOKEN_FILE):
    """Load tokens from a JSON file."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return None

def save_tokens(tokens, filename=IRC_TOKEN_FILE):
    """Save tokens to a JSON file."""
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)  # Create the directory if it doesn't exist
    with open(filename, "w") as file:
        json.dump(tokens, file)

def is_token_expired(tokens):
    """Check if the access token is expired."""
    from datetime import datetime, timedelta
    token_age = timedelta(seconds=tokens["expires_in"])
    token_creation_time = datetime.fromtimestamp(os.path.getmtime(IRC_TOKEN_FILE))
    return datetime.now() > token_creation_time + token_age

def get_valid_access_token(client_id, client_secret):
    """Ensure a valid access token by refreshing it if needed."""
    tokens = load_tokens()
    if tokens is None or is_token_expired(tokens):
        # Refresh the token
        print("Refreshing access token...")
        refreshed_tokens = refresh_user_access_token(client_id, client_secret, tokens["refresh_token"])
        save_tokens(refreshed_tokens)
        return refreshed_tokens["access_token"]
    return tokens["access_token"]

def refresh_user_access_token(client_id, client_secret, refresh_token):
    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()  # Contains new access_token and refresh_token
    else:
        raise Exception(f"Failed to refresh token: {response.status_code}, {response.text}")


