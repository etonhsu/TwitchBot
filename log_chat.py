import socket
import os
from datetime import datetime, UTC
from dotenv import load_dotenv
from auth.irc_auth import get_valid_access_token

# Load environment variables from .env file
load_dotenv()

def connect_to_chat(oauth_token, bot_username, streamer_username):
    """
    Connects to Twitch IRC chat using the provided credentials.
    """
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


def log_chat_messages(sock, streamer_username, log_buffer):
    try:
        while True:
            response = sock.recv(2048).decode('utf-8')

            # Respond to PING to keep the connection alive
            if response.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))

            # Parse chat messages
            elif "PRIVMSG" in response:
                parts = response.split(' ', 3)
                username = parts[0].split('!')[0][1:]
                message = parts[3][1:].strip()
                timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

                formatted_message = f"[{timestamp}] {username}: {message}"
                print(formatted_message)
                log_buffer.append(formatted_message)
    except KeyboardInterrupt:
        print("Exiting... Saving log.")
        save_log_to_file(streamer_username, log_buffer)
        sock.close()
    except Exception as e:
        print(f"Error: {e}")
        sock.close()


def save_log_to_file(streamer_username, log_buffer):
    """Save the buffered log messages to a file."""
    filename = f"{streamer_username}_chat_log.txt"
    try:
        with open(filename, "a") as log_file:
            for message in log_buffer:
                log_file.write(message + "\n")
        print(f"Chat log saved to {filename}")
    except Exception as e:
        print(f"Failed to save chat log: {e}")

def print_chat_messages(sock):
    """
    Continuously listens for chat messages and prints them.
    """
    try:
        while True:
            response = sock.recv(2048).decode('utf-8')

            # Respond to PING to keep the connection alive
            if response.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))

            # Parse and print chat messages
            elif "PRIVMSG" in response:
                # Extract username and message
                parts = response.split(' ', 3)
                username = parts[0].split('!')[0][1:]
                message = parts[3][1:].strip()
                timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

                # Print the formatted chat message
                print(f"[{timestamp}] {username}: {message}")

    except KeyboardInterrupt:
        print("Exiting chat listener...")
        sock.close()
    except Exception as e:
        print(f"Error: {e}")
        sock.close()


# Environment variables
client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")
bot_username = "testbot"
streamer_username = "k3soju"


oauth_token = get_valid_access_token(client_id, client_secret)

# Connect to Twitch chat and start listening
try:
    sock = connect_to_chat(oauth_token, bot_username, streamer_username)
    print_chat_messages(sock)
except Exception as e:
    print(f"Unexpected error: {e}")
