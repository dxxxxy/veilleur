import instaloader
from dotenv import load_dotenv
from instaloader import Profile

from src.utils import compute_lost, format_message, load, save, send_sms


def main():
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
    follower_ids = set([follower.userid for follower in profile.get_followers()])

    # who you follow
    followee_ids = set([followee.userid for followee in profile.get_followees()])

    # read previous followers and followees from files
    previous_follower_ids = set(load("followers.json"))
    previous_followee_ids = set(load("followees.json"))

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
    save("followers.json", follower_ids)
    save("followees.json", followee_ids)


if __name__ == "__main__":
    main()
