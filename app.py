import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message, send_image_url

load_dotenv()


machine = TocMachine(
    states=["user", "CLstate", "showfsm", "tutorial", "dribble", "shooting", "passing", "dribble2", "passing2", "shooting2"],
    transitions=[
        {
            "trigger": "advance",
            "source": ["user", "showfsm", "tutorial"],
            "dest": "CLstate",
            "conditions": "is_going_to_CLstate",
        },
        {
            "trigger": "advance",
            "source": "CLstate",
            "dest": "CLstate",
            "conditions": "is_CLprev",
        },
        {
            "trigger": "advance",
            "source": "CLstate",
            "dest": "CLstate",
            "conditions": "is_CLnext",
        },
        {
            "trigger": "advance",
            "source": ["CLstate", "showfsm", "tutorial", "dribble", "shooting", "passing", "dribble2", "passing2", "shooting2"],
            "dest": "user",
            "conditions": "is_going_to_user",
        },
        {
            "trigger": "advance",
            "source": ["user", "CLstate", "tutorial"],
            "dest": "showfsm",
            "conditions": "is_going_to_showfsm",
        },
        {
            "trigger": "advance",
            "source": ["user", "showfsm", "CLstate", "dribble", "shooting", "passing", "dribble2", "passing2", "shooting2"],
            "dest": "tutorial",
            "conditions": "is_going_to_tutorial",
        },
        {
            "trigger": "advance",
            "source": ["tutorial", "shooting", "passing"],
            "dest": "dribble",
            "conditions": "is_going_to_dribble",
        },
        {
            "trigger": "advance",
            "source": ["tutorial", "dribble", "passing"],
            "dest": "shooting",
            "conditions": "is_going_to_shooting",
        },
        {
            "trigger": "advance",
            "source": ["tutorial", "shooting", "dribble"],
            "dest": "passing",
            "conditions": "is_going_to_passing",
        },
        {
            "trigger": "advance",
            "source": "dribble",
            "dest": "dribble2",
            "conditions": "is_going_to_dribble2",
        },
        {
            "trigger": "advance",
            "source": "shooting",
            "dest": "shooting2",
            "conditions": "is_going_to_shooting2",
        },
        {
            "trigger": "advance",
            "source": "passing",
            "dest": "passing2",
            "conditions": "is_going_to_passing2",
        },
        #{"trigger": "go_back", "source": ["CLprev", "state3"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)
    # print("Request body: " + body, "Signature: " + signature)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        # print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")
    """
    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )
    """
    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
