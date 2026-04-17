import json
import os

from twilio.rest import Client


def compute_lost(previous, current):
    return set(previous) - set(current)


def format_message(lost_followers, lost_followees):
    message = "\n\nveilleur update:\n\n"

    if lost_followers:
        message += f"Lost Followers: {', '.join(map(str, lost_followers))}\n"

    if lost_followees:
        message += f"Lost Followees: {', '.join(map(str, lost_followees))}\n"

    message += "\n\ni love you so much baby <3 —yours truly"
    return message


def load(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"No previous data found at {path}, starting fresh.")
        return None


def save(path, content):
    # json cannot save set
    if isinstance(content, set):
        content = list(content)

    with open(path, "w") as f:
        json.dump(content, f)


def send_sms(content):
    # setup twilio client
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    if not account_sid or not auth_token:
        print("Twilio credentials not set in environment variables. Skipping SMS notification. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")
        return False

    client = Client(account_sid, auth_token)

    # setup twilio phone numbers
    from_phone = os.getenv('TWILIO_FROM_PHONE')
    to_phone = os.getenv('TWILIO_TO_PHONE')

    if not from_phone or not to_phone:
        print("Twilio phone numbers not set in environment variables. Skipping SMS notification. Please set TWILIO_FROM_PHONE and TWILIO_TO_PHONE.")
        return False

    # send the message
    client.messages.create(
        body=content,
        from_=from_phone,
        to=to_phone
    )

    return True
