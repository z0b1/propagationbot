import os 
import threading
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app= Flask(__name__)

user_client = WebClient(token=os.getenv("SLACK_USER_TOKEN"))
rsvpl = "https://propagation.z0b1.tech"

def send_welcome_message(user_id, channel_id):
    try:
        user_client.chat_postMessage(
            channel=channel_id,
            text=f"Welcome to Propagation!",
            blocks=[
                {
                    "type":"section",
                    "text":{
                        "type":"mrkdwn",
                        "text":f"Hey <@{user_id}>! Welcome to Propagation! We are super excited to have you ship and build your project."
                    }
                },
                {
                    "type":"actions",
                    "elements":[
                        {
                            "type":"button",
                            "text":{
                                "type":"plain_text",
                                "text":"Visit our website"
                            },
                            "url":rsvpl
                        }
                    ]



                    }
                    

                
                ]
        )
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
@app.route("/", methods=["POST"])
@app.route("/", methods=["GET", "POST"])  

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
            
            threading.Thread(
                target=send_welcome_message, 
                args=(user_id, channel_id)
            ).start()
            
    return jsonify({"status": "ok"}), 200
