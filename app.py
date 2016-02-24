#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import our required modules:
import atexit
import bots
import time

# Create instances of our two classes:
emailbot = bots.EmailBot()
redditbot = bots.RedditBot('todayilearned')

# Handles the program exiting: the message is printed and the file containg 
# the ids of the facts already sent is closed and saved for next time
def exit_handler():
    print 'The program will now shut down.'
    redditbot.already_sent.close()

# Main function: takes and EmailBot instance, redditBot instance, 
# the number of emails to be sent to the user, and
# the time to sleep in between running, as arguments.
# Carries out the RedditBot run method, until the amount of
# emails to be sent to the user has been reached, and sleeps for
# the specified time between each run.
def main(embot_instance,rbot_instance,no_of_emails,sleep_time):
    atexit.register(exit_handler)
    no_of_emails_sent = 0
    while no_of_emails_sent < no_of_emails:
        rbot_instance.run(embot_instance)
        no_of_emails_sent += 1
        time.sleep(sleep_time)

# Call our main function (for testing purposes the last two parameters can be changed):
if __name__ == '__main__':
    main(emailbot, redditbot, 12, 60*30)

