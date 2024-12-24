import threading
import os

from auth.api_auth import get_streamer_id
from helper_functions.log_chat import connect_to_chat, manage_intervals
from eventsub.eventsub_api import verify_eventsub
from eventsub.eventsub_webhook import app

# Environment variables
bot_username = "testbot"
streamer_username = "dishsoap"

def start_webhook_server():
    """
    Starts the Flask app for EventSub webhook handling in a separate thread.
    """
    app.run(port=5000, debug=False, use_reloader=False)

def main():
    """
    Main script to manage EventSub subscriptions, start the webhook server,
    connect to chat, and manage interval-based logging.
    """
    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")

    # Step 1: Get Streamer ID
    print(f"Fetching ID for {streamer_username}...")
    streamer_id = get_streamer_id(client_id, client_secret, streamer_username)
    print(f"Streamer ID: {streamer_id}")

    # # Step 2: Verify EventSub Subscriptions
    # print("Verifying EventSub subscriptions...")
    # verify_eventsub(streamer_id)

    # Step 3: Start Webhook Server
    print("Starting EventSub webhook server...")
    webhook_thread = threading.Thread(target=start_webhook_server, daemon=True)
    webhook_thread.start()

    # Step 4: Connect to Twitch Chat
    print(f"Connecting to {streamer_username}'s chat...")
    sock = connect_to_chat(bot_username, streamer_username)

    # Step 5: Manage Intervals for Logging
    print(f"Starting to log chat messages and interval data for {streamer_username}...")
    try:
        manage_intervals(sock, streamer_username, interval_minutes=10)
    except KeyboardInterrupt:
        print("Shutting down...")
        sock.close()
        webhook_thread.join()

if __name__ == "__main__":
    main()
