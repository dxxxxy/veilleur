import json
import os

import instaloader
from dotenv import load_dotenv
from instaloader import Profile

# load environment variables from .env file
load_dotenv()

# initialize instaloader
insta = instaloader.Instaloader()

# enter username
username = input("Enter Instagram username: ")

# load session if it exists, otherwise do interactive login and save session for future use
try:
    insta.load_session_from_file(username, "session")
except FileNotFoundError:
    insta.interactive_login(username)
    insta.save_session_to_file("session")

# get your own profile
profile = Profile.own_profile(insta.context)

# who follows you
follower_ids = [follower.userid for follower in profile.get_followers()]

# who you follow
followee_ids = [followee.userid for followee in profile.get_followees()]

# try to read previous followers and followees from files, if they exist, and store them in sets for comparison
previous_followers = set()
previous_followees = set()
try:
    with open("followers.json", "r") as f:
        previous_followers = set(json.load(f))

    with open("followees.json", "r") as f:
        previous_followees = set(json.load(f))
except FileNotFoundError:
    print("No previous follower/followee data found, starting fresh.")

# compute lost followers and followees by comparing the current sets with the previous sets
if previous_followers and previous_followees:
    lost_followers = previous_followers - set(follower_ids)
    lost_followees = previous_followees - set(followee_ids)

    # send message to twilio if there are any lost followers or followees
    if lost_followers or lost_followees:
        from twilio.rest import Client

        # setup twilio client
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')

        if not account_sid or not auth_token:
            print("Twilio credentials not set in environment variables. Skipping SMS notification.")
            exit(0)

        client = Client(account_sid, auth_token)

        # setup twilio phone numbers
        from_phone = os.getenv('TWILIO_FROM_PHONE')
        to_phone = os.getenv('TWILIO_TO_PHONE')

        if not from_phone or not to_phone:
            print("Twilio phone numbers not set in environment variables. Skipping SMS notification.")
            exit(0)

        # create message body
        message_body = "\n\nveilleur update:\n"
        if lost_followers:
            message_body += f"Lost Followers: {', '.join(str(uid) for uid in lost_followers)}\n"
        if lost_followees:
            message_body += f"Lost Followees: {', '.join(str(uid) for uid in lost_followees)}\n"
        message_body += "\n\ni love you so much baby <3 —yours truly"

        # Send the message
        message = client.messages.create(
            body=message_body,
            from_=from_phone,
            to=to_phone
        )

# update current followers
with open("followers.json", "w") as f:
    json.dump(follower_ids, f)

# update current followees
with open("followees.json", "w") as f:
    json.dump(followee_ids, f)
