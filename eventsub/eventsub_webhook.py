import os
import json
import hmac
import hashlib
from flask import Flask, request
from threading import Lock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitch credentials
twitch_secret = os.getenv("TWITCH_WEBHOOK_SECRET")  # A secret to validate incoming requests

# Shared counters for subscribers and followers
data_lock = Lock()
subscribers_gained = 0
followers_gained = 0

# Flask app for webhook handling
app = Flask(__name__)

# Verify the Twitch signature
def verify_signature(headers, body):
    message_id = headers.get("Twitch-Eventsub-Message-Id")
    timestamp = headers.get("Twitch-Eventsub-Message-Timestamp")
    signature = headers.get("Twitch-Eventsub-Message-Signature")
    message = message_id + timestamp + body

    # Generate HMAC SHA256 signature
    hmac_signature = hmac.new(twitch_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    expected_signature = f"sha256={hmac_signature}"

    return hmac.compare_digest(expected_signature, signature)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    global subscribers_gained, followers_gained

    headers = request.headers
    body = request.data.decode("utf-8")

    # Verify the signature
    if not verify_signature(headers, body):
        return "Invalid signature", 403

    # Handle verification challenge
    if headers.get("Twitch-Eventsub-Message-Type") == "webhook_callback_verification":
        challenge = json.loads(body)["challenge"]
        return challenge, 200

    # Handle notifications
    if headers.get("Twitch-Eventsub-Message-Type") == "notification":
        notification = json.loads(body)
        event_type = notification["subscription"]["type"]
        event = notification["event"]

        if event_type == "channel.subscribe":
            with data_lock:
                subscribers_gained += 1
            print(f"New subscriber: {event['user_name']}")
        elif event_type == "channel.follow":
            with data_lock:
                followers_gained += 1
            print(f"New follower: {event['user_name']}")

        return "OK", 200

    return "Unhandled message type", 400

# Get the counters and reset them
def get_and_reset_counters():
    global subscribers_gained, followers_gained
    with data_lock:
        subs, followers = subscribers_gained, followers_gained
        subscribers_gained, followers_gained = 0, 0  # Reset counters
    return subs, followers

if __name__ == "__main__":
    app.run(port=5000)