#!/usr/bin/python
# -*- coding: utf-8 -*-
# Tidied up using PythonTidy

# Import our required modules:
from django.utils.encoding import smart_str
import getpass
import json
import praw
import requests
import smtplib
import sys
import urllib


class EmailBot(object):
    # Gets the username and password and sets up the Gmail connection
    def __init__(self):
        self.username = \
            raw_input('Please enter your Gmail address and hit Enter: ')
        self.password = \
            getpass.getpass('Please enter the password for this email account and hit Enter: '
                            )
        self.server = 'smtp.gmail.com'
        self.port = 587
        print 'Connecting to the server. Please wait a moment...'

        try:
            self.session = smtplib.SMTP(self.server, self.port)
            self.session.ehlo()  # Identifying ourself to the server
            self.session.starttls()  # Puts the SMTP connection in TLS mode. All SMTP commands that follow will be encrypted
            self.session.ehlo()
        except smtplib.socket.gaierror:
            print 'Error connecting. Please try running the program again later.'
            sys.exit() # The program will cleanly exit in such an error

        try:
            self.session.login(self.username, self.password)
            del self.password
        except smtplib.SMTPAuthenticationError:
            print 'Invalid username (%s) and/or password. Please try running the program again later.'\
                 % self.username
            sys.exit() # program will cleanly exit in such an error

    def send_message(self, subject, body):
        try:
            headers = ['From: ' + self.username, 'Subject: ' + subject,
                       'To: ' + self.username, 'MIME-Version: 1.0',
                       'Content-Type: text/html']
            headers = '\r\n'.join(headers)

            self.session.sendmail(self.username, self.username, headers
                                   + '''\r
\r
''' + body)
        except smtplib.socket.timeout:
            print 'Socket error while sending message. Please try running the program again later.'
            sys.exit() # Program claanly exits
        except:
            print "Couldn't send message. Please try running the program again later."
            sys.exit() # Program cleanly exits


class RedditBot(object):
    # Gets the keywords to search for and sets up the connection with the subreddit
    def __init__(self, chosen_subreddit):
        self.ask_keywords = \
            raw_input('Please enter the keywords you would like the bot to search for and press Enter.\nNote: each word must be separated with a comma, with no spaces: ')
        self.keywords = self.ask_keywords.split(',') # puts each keyword entered into a list for the bot to check the reddit facts for
        self.already_sent = open('already_sent.txt', 'ab+')
        self.emailed_already = self.already_sent.readlines() # creates a list of all the items in the file
        self.chosen_subreddit = chosen_subreddit
        self.reddit = praw.Reddit(user_agent="Andrew's reddit/email bot"
                                  )
        self.subreddit = self.reddit.get_subreddit(chosen_subreddit)

    # Checks the fact for profanity using the online wdyl profanity checker
    def check_profanity(self, fact_to_check):
        try:
            self.fact_to_check = fact_to_check
            self.connection = \
                urllib.urlopen('http://www.wdyl.com/profanity?q='
                                + smart_str(fact_to_check))
            self.output = self.connection.read()
            self.connection.close()
            if 'true' in self.output:  # ie if the fact contains a curse word; the bot moves on to search for another fact
                return True
            else:
                return False  # ie if it does not contain a curse word
        except:
            return True # if a error occurs, the bot simply treats it as a curse word, and moves on to search for another fact

    # Shortens the input url using the online goo.gl url shortener
    def shorten(self, url):
        try:
            # Specifies the data to be sent to the service
            self.url = smart_str(url)
            self.headers = {'content-type': 'application/json'}
            self.payload = {'longUrl': url}
            self.url_2 = \
                'https://www.googleapis.com/urlshortener/v1/url'
            self.r = requests.post(self.url_2,
                                   data=json.dumps(self.payload),
                                   headers=self.headers)
            if 'id' in json.loads(self.r.text): # ie if there is no error and we get a dictionary with the shortened url in it
                self.link = json.loads(self.r.text)['id']
            else:
                self.link = self.url # if there is an error we simply return the original url
            return self.link
        except:
            return self.url # if we get a different type of error error, it simply returns the original, unshortened url

    # Looks for the first fact that has contains one or more keywords, has no profanity and hasn't already been sent; 
    # when one does, an email is sent and the id is appoended to the file and the list 
    # so the progranm knows it has already been sent, and the method stops, until we invoke it the next time       
    def run(self, emailbot_instance):
        print 'The bot is now checking reddit for facts containing your specified keywords.'
        try:
            for submission in self.subreddit.get_hot(limit=None): # goes through all the facts in the subreddit
                for word in self.keywords: # goes through each inputted keyword
                    if word in submission.title.split()\
                         and str(submission.id) + '\n'\
                         not in self.emailed_already:
                        if not self.check_profanity(submission.title):
                            emailbot_instance.send_message('New Fact!!!'
                                    , '%s <br> <br> Source: %s'
                                     % (smart_str(submission.title),
                                    smart_str(self.shorten(smart_str(submission.url)))))
                            self.emailed_already.append(str(submission.id)
                                     + '\n')
                            self.already_sent.write(str(submission.id)
                                     + '\n')
                            print 'An email was just sent to your account!'
                            return 
        except:
            self.emailed_already.append(str(submission.id) + '\n') # if we get an error, the fact is treated as already sent, so we do not come across it and try rto send it again
            return


