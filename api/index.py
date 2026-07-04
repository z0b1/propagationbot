import os
import threading
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = Flask(__name__)

user_client = WebClient(token=os.getenv("SLACK_USER_TOKEN"))
MY_SLACK_ID = os.getenv("MY_SLACK_ID")
RSVP_LINK = "https://propagation.z0b1.tech"


def send_welcome_message(user_id, channel_id):
    try:
        user_client.chat_postMessage(
            channel=channel_id,
            text="Welcome to Propagation!",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hey <@{user_id}>! Welcome to Propagation! We are super excited to have you ship and build your project."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Visit our website"},
                            "url": RSVP_LINK
                        }
                    ]
                }
            ]
        )
    except SlackApiError as e:
        print(f"Welcome message error: {e.response['error']}")


def send_help_dm(user_id):
    try:
        dm = user_client.conversations_open(users=user_id)
        dm_channel_id = dm["channel"]["id"]
        user_client.chat_postMessage(
            channel=dm_channel_id,
            text="Hiya, I am Propagation bot! Here's the help guide!",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Propagation Commands*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            "Here's what I can do:\n\n"
                            "• `help` — Sends you this guide.\n"
                            "• `rsvp` — Sends you the website link.\n"
                            "• `ship` — Sends you the link to ship your project.\n"
                            "• `shipguide` — Sends you the shipping guide.\n"
                            "• `structure` — Sends you the starstruct app link.\n\n"
                            "Have fun building and shipping! If you have any questions, feel free to reach out to the Propagation team."
                        )
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Visit our website"},
                            "url": RSVP_LINK
                        }
                    ]
                }
            ]
        )
    except SlackApiError as e:
        print(f"Help DM error: {e.response['error']}")


def send_rsvp_dm(user_id):
    try:
        dm = user_client.conversations_open(users=user_id)
        dm_channel_id = dm["channel"]["id"]
        user_client.chat_postMessage(
            channel=dm_channel_id,
            text="Here's the Propagation website!",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Here's the link to the Propagation website!"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Visit our website"},
                            "url": RSVP_LINK
                        }
                    ]
                }
            ]
        )
    except SlackApiError as e:
        print(f"RSVP DM error: {e.response['error']}")


@app.route("/", methods=["GET", "POST"])
def send_unknown_dm(user_id):
    try:
        dm = user_client.conversations_open(users=user_id)
        dm_channel_id = dm["channel"]["id"]
        user_client.chat_postMessage(
            channel=dm_channel_id,
            text="That frequency is not on my spectrum.",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📡 That frequency is not on my spectrum.\n\nTry `help` to see what I can do!"
                    }
                }
            ]
        )
    except SlackApiError as e:
        print(f"Unknown command DM error: {e.response['error']}")
def slack_events():
    if request.method == "GET":
        return jsonify({"status": "Selfbot server is running smoothly!"}), 200

    data = request.json

    if data and "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    if data and "event" in data:
        event = data["event"]
        event_type = event.get("type")

        if event_type == "member_joined_channel":
            user_id = event.get("user")
            channel_id = event.get("channel")
            threading.Thread(target=send_welcome_message, args=(user_id, channel_id)).start()

        elif event_type == "message":
            # Skip edits, deletions, bot messages
            if event.get("subtype") is not None or "bot_id" in event:
                return jsonify({"status": "ok"}), 200

            user_id = event.get("user")

            # Skip your own messages to prevent infinite loop
            if user_id == MY_SLACK_ID:
                return jsonify({"status": "ok"}), 200

            text = event.get("text", "").lower().strip()

            if text in ["help", "!help", "commands"]:
                threading.Thread(target=send_help_dm, args=(user_id,)).start()

            elif text in ["rsvp", "!rsvp", "website"]:
                threading.Thread(target=send_rsvp_dm, args=(user_id,)).start()

            elif text.startswith("!") or text in ["ship", "shipguide", "structure"]:
                threading.Thread(target=send_unknown_dm, args=(user_id,)).start()

    return jsonify({"status": "ok"}), 200