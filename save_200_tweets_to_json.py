#!/usr/bin/env python

"""
This script downloads all available Tweets for a given list of
usernames.

The script takes as input a text file which lists one Twitter username
per line of the file.  The script creates a [username].tweets file for
each username specified in the directory.

Your Twitter OAuth credentials should be stored in the file
twitter_oauth_settings.py.
"""

# Standard Library modules
import argparse
import codecs
import os
import sys

# Third party modules
from twython import Twython, TwythonError

# Local modules
from twitter_crawler import (CrawlTwitterTimelines, RateLimitedTwitterEndpoint, 
                             get_console_info_logger, get_screen_names_from_file, save_tweets_to_json_file)
try:
    from twitter_oauth_settings import access_token, access_token_secret, consumer_key, consumer_secret
except ImportError:
    print "You must create a 'twitter_oauth_settings.py' file with your Twitter API credentials."
    print "Please copy over the sample configuration file:"
    print "  cp twitter_oauth_settings.sample.py twitter_oauth_settings.py"
    print "and add your API credentials to the file."
    sys.exit()


def main():
    # Make stdout output UTF-8, preventing "'ascii' codec can't encode" errors
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = argparse.ArgumentParser(description="")
    parser.add_argument('screen_name_file')
    args = parser.parse_args()

    logger = get_console_info_logger()

    ACCESS_TOKEN = Twython(consumer_key, consumer_secret, oauth_version=2).obtain_access_token()
    twython = Twython(consumer_key, access_token=ACCESS_TOKEN)

    crawler = RateLimitedTwitterEndpoint(twython, "statuses/user_timeline", logger)

    screen_names = get_screen_names_from_file(args.screen_name_file)

    for screen_name in screen_names:
        tweet_filename = "%s.tweets" % screen_name
        if os.path.exists(tweet_filename):
            logger.info("File '%s' already exists - will not attempt to download Tweets for '%s'" % (tweet_filename, screen_name))
        else:
            try:
                logger.info("Retrieving Tweets for user '%s'" % screen_name)
                tweets = crawler.get_data(screen_name=screen_name, count=200)
            except TwythonError as e:
                print "TwythonError: %s" % e
                if e.error_code == 404:
                    logger.warn("HTTP 404 error - Most likely, Twitter user '%s' no longer exists" % screen_name)
                elif e.error_code == 401:
                    logger.warn("HTTP 401 error - Most likely, Twitter user '%s' no longer publicly accessible" % screen_name)
                else:
                    # Unhandled exception
                    raise e
            else:
                save_tweets_to_json_file(tweets, "%s.tweets" % screen_name)


if __name__ == "__main__":
    main()
