"""
"""

import codecs
import json
import logging
import os
import re
import sys

# Third party modules
from twython import TwythonError

# Local modules
from tweet_filter import TweetFilter
from twitter_crawler import RateLimitedTwitterEndpoint, save_tweets_to_json_file


class TweetFilterTimelineDownloadable(TweetFilter):
    def __init__(self, twython, download_path, minimum_tweet_threshold, logger=None):
        self._crawler = RateLimitedTwitterEndpoint(twython, "statuses/user_timeline", logger)
        self._download_path = download_path
        self._minimum_tweet_threshold = minimum_tweet_threshold
        self._twython = twython
        TweetFilter.__init__(self, logger=logger)

    def filter(self, json_tweet_string):
        tweet = json.loads(json_tweet_string)
        screen_name = tweet['user']['screen_name']

        path_to_tweetfile = os.path.join(self._download_path, "%s.tweets" % screen_name)

        # If file already exists for user, don't try to rescrape their timeline
        if os.path.exists(path_to_tweetfile):
            self._logger.info("Timeline file for '%s' already exists - will not rescrape" % screen_name)
            if os.path.getsize(path_to_tweetfile) > 0:
                return True
            else:
                return False

        try:
            self._logger.info("Retrieving Tweets for user '%s'" % screen_name)
            tweets = self._crawler.get_data(screen_name=screen_name, count=200)
        except TwythonError as e:
            print "TwythonError: %s" % e
            if e.error_code == 404:
                self._logger.warn("HTTP 404 error - Most likely, Twitter user '%s' no longer exists" % screen_name)
                open(path_to_tweetfile, "w").close()   # Create empty file
                return False
            elif e.error_code == 401:
                self._logger.warn("HTTP 401 error - Most likely, Twitter user '%s' no longer publicly accessible" % screen_name)
                open(path_to_tweetfile, "w").close()   # Create empty file
                return False
            else:
                # Unhandled exception
                raise e
        else:
            if len(tweets) < self._minimum_tweet_threshold:
                self._logger.info("User '%s' has only %d Tweets, threshold is %d" % \
                                      (screen_name, len(tweets), self._minimum_tweet_threshold))
                open(path_to_tweetfile, "w").close()   # Create empty file
                return False
            else:
                save_tweets_to_json_file(tweets, path_to_tweetfile)
                return True
