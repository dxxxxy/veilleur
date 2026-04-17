import os
import sys

import instaloader
from dotenv import load_dotenv
from instaloader import Profile, TwoFactorAuthRequiredException

from src.utils import compute_lost, format_message, load, save, send_sms


def main(two_factor_code):
    # load environment variables from .env file
    load_dotenv()

    # initialize instaloader
    insta = instaloader.Instaloader()

    # get instagram credentials from environment variables
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")

    if not username or not password:
        print(
            "Instagram credentials not set in environment variables. Please set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD.")
        return

    # load session if it exists, otherwise do interactive login and save session for future use
    try:
        insta.load_session_from_file(username, f"session_{username}")
    except FileNotFoundError:
        try:
            insta.login(username, password)
        except TwoFactorAuthRequiredException:
            if not two_factor_code:
                print(
                    "Two-factor authentication is enabled for this account. Please provide the two-factor authentication code as a command-line argument.")
                return

            try:
                insta.two_factor_login(two_factor_code)
            except Exception as e:
                print(f"Two-factor authentication failed: {e}")
                return

        insta.save_session_to_file(f"session_{username}")

    # get profile
    profile_id = os.getenv("INSTAGRAM_PROFILE_ID")

    if not profile_id:
        print("Instagram profile ID not set in environment variables. Using own profile. Please set INSTAGRAM_PROFILE_ID.")
        profile = Profile.own_profile(insta.context)
    else:
        profile = Profile.from_username(insta.context, profile_id)

    # who follows you
    follower_ids = set([follower.userid for follower in profile.get_followers()])

    # who you follow
    followee_ids = set([followee.userid for followee in profile.get_followees()])

    # read previous followers and followees from files
    previous_follower_ids = set(load(f"followers_{profile_id}.json"))
    previous_followee_ids = set(load(f"followees_{profile_id}.json"))

    # if we have all data required for comparison, continue
    if previous_follower_ids and previous_followee_ids:
        # compute lost followers and followees
        lost_followers = compute_lost(previous_follower_ids, follower_ids)
        lost_followees = compute_lost(previous_followee_ids, followee_ids)

        # if we have any lost followers or followees, continue
        if lost_followers or lost_followees:
            # try to send twilio sms notification, otherwise just print in console
            if send_sms(format_message(lost_followers, lost_followees)):
                print("SMS notification sent successfully.")
            else:
                print(format_message(lost_followers, lost_followees))
        else:
            print("No lost followers or followees since last check.")

    # update current followers and followees
    save(f"followers_{profile_id}.json", follower_ids)
    save(f"followees_{profile_id}.json", followee_ids)


if __name__ == "__main__":
    print("Running veilleur...")
    main(sys.argv[1] if len(sys.argv) > 1 else None)
