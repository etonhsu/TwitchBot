import socket
import json
import os
from datetime import datetime, timedelta, UTC
from threading import Event, Thread
from dotenv import load_dotenv

from auth.irc_auth import get_valid_access_token
from eventsub.eventsub_webhook import get_and_reset_counters
from helper_functions.view_count import check_viewership

# Load environment variables from .env file
load_dotenv()


def connect_to_chat(bot_username, streamer_username):
    """
    Connects to Twitch IRC chat using the provided credentials.
    """
    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")
    oauth_token = get_valid_access_token(client_id, client_secret)

    server = 'irc.chat.twitch.tv'
    port = 6667  # Non-SSL port

    # Connect to the Twitch IRC server
    sock = socket.socket()
    sock.connect((server, port))

    # Authenticate and join the chat
    sock.send(f"PASS oauth:{oauth_token}\n".encode('utf-8'))
    sock.send(f"NICK {bot_username}\n".encode('utf-8'))
    sock.send(f"JOIN #{streamer_username}\n".encode('utf-8'))

    print(f"Connected to {streamer_username}'s chat!")
    return sock


def log_chat_messages(sock, log_buffer, interval_end_event):
    """
    Records all chat messages including username and timestamp
    """
    try:
        while True:
            response = sock.recv(2048).decode('utf-8')

            if response.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))
            elif "PRIVMSG" in response:
                parts = response.split(' ', 3)
                username = parts[0].split('!')[0][1:]
                message = parts[3][1:].strip()
                timestamp = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

                log_buffer.append({"timestamp": timestamp, "username": username, "message": message})

                print(f"[{timestamp}] {username}: {message}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        interval_end_event.set()  # Signal end of logging
        sock.close()


def save_to_single_file(streamer_username, interval_data):
    """
    Appends interval data to a single JSON file.
    """
    filename = f"{streamer_username}_chat_log.json"

    # Load existing data
    if os.path.exists(filename):
        with open(filename, "r") as file:
            all_data = json.load(file)
    else:
        all_data = []  # Start with an empty list if the file doesn't exist

    # Append the new interval data
    all_data.append(interval_data)

    # Write the updated data back to the file
    with open(filename, "w") as file:
        json.dump(all_data, file, indent=4)

    print(f"Appended data for interval starting at {interval_data['start_time']} to {filename}")


def manage_intervals(sock, streamer_username, interval_minutes=10):
    """
    Determines the interval recorded and notes viewers, subscribers gained, and followers gained in that time
    """
    log_buffer = []
    interval_start = datetime.now(UTC)

    while True:
        try:
            interval_end = interval_start + timedelta(minutes=interval_minutes)

            # Wait for the interval to finish
            interval_end_event = Event()
            logging_thread = Thread(target=log_chat_messages, args=(sock, log_buffer, interval_end_event))
            logging_thread.start()

            while datetime.now(UTC) < interval_end:
                interval_end_event.wait(timeout=1)

            # Check viewership using Twitch API
            viewers = check_viewership(streamer_username)

            # Get subscribers and followers from the webhook counters
            subs_gained, followers_gained = 5, 10

            # Prepare interval data
            interval_data = {
                "start_time": interval_start.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "end_time": interval_end.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "chat_logs": log_buffer,
                "viewers": viewers,
                "subscribers_gained": subs_gained,
                "followers_gained": followers_gained
            }

            # Save to a single JSON file
            save_to_single_file(streamer_username, interval_data)

            # Reset for the next interval
            interval_start = interval_end
            log_buffer.clear()

        except KeyboardInterrupt:
            print("Exiting interval manager...")
            sock.close()
            break
        except Exception as e:
            print(f"Error in interval manager: {e}")
            sock.close()
            break



