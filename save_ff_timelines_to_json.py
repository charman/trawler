#!/usr/bin/env python

"""
This script downloads all available Tweets from the one-hop network
for a given list of usernames.  For a given Twitter user, only other
users who are both Friends and Followers (e.g. have a reciprocal
relationship) are considered to be part of the one-hop network.

For each username in the provided list, the script creates a
[username].ff file that contains the friends-and-followers screen
names (one screen name per line) for the specified Twitter user.

The script creates a [username].tweets file containing the Tweets (one
JSON object per line) for each user who is a friend-and-follower of
one of the provided users..

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
from twitter_crawler import (CrawlTwitterTimelines, FindFriendFollowers, RateLimitedTwitterEndpoint,
                             get_console_info_logger, get_screen_names_from_file, 
                             save_screen_names_to_file, save_tweets_to_json_file)
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

    timeline_crawler = CrawlTwitterTimelines(twython, logger)
    ff_finder = FindFriendFollowers(twython, logger)

    screen_names = get_screen_names_from_file(args.screen_name_file)

    for screen_name in screen_names:
        ff_screen_names = ff_finder.get_ff_screen_names_for_screen_name(screen_name)
        save_screen_names_to_file(ff_screen_names, "%s.ff" % screen_name, logger)

        for ff_screen_name in ff_screen_names:
            tweet_filename = "%s.tweets" % ff_screen_name
            if os.path.exists(tweet_filename):
                logger.info("File '%s' already exists - will not attempt to download Tweets for '%s'" % (tweet_filename, ff_screen_name))
            else:
                try:
                    tweets = timeline_crawler.get_all_timeline_tweets_for_screen_name(ff_screen_name)
                except TwythonError as e:
                    print "TwythonError: %s" % e
                    if e.error_code == 404:
                        logger.warn("HTTP 404 error - Most likely, Twitter user '%s' no longer exists" % ff_screen_name)
                    elif e.error_code == 401:
                        logger.warn("HTTP 401 error - Most likely, Twitter user '%s' no longer publicly accessible" % ff_screen_name)
                    else:
                        # Unhandled exception
                        raise e
                else:
                    save_tweets_to_json_file(tweets, tweet_filename)



if __name__ == "__main__":
    main()
