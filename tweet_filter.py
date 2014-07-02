"""
"""

import codecs
import json
import logging
import re

# Chromium Compact Language Detector
#   https://pypi.python.org/pypi/chromium_compact_language_detector/ 
import cld


class FilteredTweetReader:
    """
    Convenience class for reading only Tweets from a JSON Tweet file
    (one JSON object per line) that pass through zero or more filters.

    Usage:
      filtered_reader = FilteredTweetReader()
      filtered_reader.add_filter(TweetFilterOne())
      filtered_reader.open('tweet_filename')
      for json_tweet_string in filtered_reader:
          do_something(json_tweet_string)
    """
    def __del__(self):
        if self._tweet_file:
            self._tweet_file.close()

    def __init__(self, filters=[], logger=None):
        # First filter is always a TweetFilterValidJSON instance
        self._filters = [TweetFilterValidJSON(logger)] + filters
        self._tweet_file = None

    def __iter__(self):
        return self

    def add_filter(self, filter):
        self._filters.append(filter)

    def open(self, tweet_filename):
        self._tweet_file = codecs.open(tweet_filename, 'r', 'utf-8')

    def close(self):
        self._tweet_file.close()

    def next(self):
         while 1:
             # _tweet_file.__next__() will throw a StopIteration if EOF reached
             json_tweet_string = self._tweet_file.next()

             # Filters will stop being applied after the first filter fails
             for filter in self._filters:
                 if not filter.filter(json_tweet_string):
                     break
             # The else clause runs when no break occurs before the 'for' loop completes
             else:
                 return json_tweet_string


class TweetFilter:
    """
    Base class for other TweetFilters
    """
    def __init__(self, logger=None):
        if logger is None:
            # Log INFO and above to stderr
            self._logger = logging.getLogger()
            self._logger.setLevel(logging.INFO)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            self._logger.addHandler(console_handler)
        else:
            self._logger = logger

    def filter(self, json_tweet_string):
        raise NotImplementedError


class TweetFilterReliablyEnglish(TweetFilter):
    """
    Returns true IFF Chromium Compact Language Detector claims that Tweet is English.
    """
    def filter(self, json_tweet_string):
        tweet = json.loads(json_tweet_string)
        # CLD expects a bytestring encoded as UTF-8, and not a unicode string
        tweet_text = codecs.encode(tweet['text'], 'utf-8')
        # Per the CLD docs, "isReliable is True if the top language is much better than 2nd best language."
        topLanguageName, topLanguageCode, isReliable, textBytesFound, details = cld.detect(tweet_text)
        if topLanguageName == "ENGLISH" and isReliable:
            return True
        else:
            return False


class TweetFilterNoURLs(TweetFilter):
    def filter(self, json_tweet_string):
        tweet = json.loads(json_tweet_string)
        if re.search(r'https?://', tweet['text']):
            return False
        else:
            return True


class TweetFilterOneTweetPerScreenName(TweetFilter):
    def __init__(self, logger=None):
        self._screen_name_set = set()
        TweetFilter.__init__(self, logger=logger)

    def filter(self, json_tweet_string):
        tweet = json.loads(json_tweet_string)
        screen_name = tweet['user']['screen_name']
        if not screen_name in self._screen_name_set:
            self._screen_name_set.add(screen_name)
            return True
        else:
            return False


class TweetFilterFieldMatchesRegEx(TweetFilter):
    def __init__(self, tweet_field, regex, logger=None):
        self._regex = regex
        self._tweet_field = tweet_field
        TweetFilter.__init__(self, logger=logger)

    def filter(self, json_tweet_string):
        """
        Returns True if the Tweet field for the json_tweet_string
        matches the regex
        """
        tweet = json.loads(json_tweet_string)
        if re.search(self._regex, tweet[self._tweet_field]):
            return True
        else:
            return False


class TweetFilterIDSet(TweetFilter):
    """
    Base class for TweetFilterIDInSet and TweetFilterIDNotInSet
    """
    def __init__(self, logger=None):
        self._tweet_id_set = set()
        TweetFilter.__init__(self, logger=logger)

    def add_tweet(self, json_tweet_string):
        tweet = json.loads(json_tweet_string)
        self._tweet_id_set.add(tweet['id'])

    def add_tweets(self, json_tweet_string_list):
        for json_tweet_string in json_tweet_string_list:
            self.add_tweet(json_tweet_string)

    def add_tweet_id(self, tweet_id):
        self._tweet_id_set.add(tweet_id)

    def add_tweet_ids(self, tweet_ids):
        self._tweet_id_set.update(tweet_ids)

    def filter(self, json_tweet_string):
        raise NotImplementedError


class TweetFilterTweetIDInSet(TweetFilterIDSet):
    def filter(self, json_tweet_string):
        """
        Returns True if the Tweet's ID is in the existing set
        """
        tweet = json.loads(json_tweet_string)
        return (tweet['id'] in self._tweet_id_set) or (tweet['id_str'] in self._tweet_id_set)


class TweetFilterTweetIDNotInSet(TweetFilterIDSet):
    def filter(self, json_tweet_string):
        """
        Returns True if the Tweet's ID is not in the existing set
        """
        tweet = json.loads(json_tweet_string)
        return (tweet['id'] not in self._tweet_id_set) and (tweet['id_str'] not in self._tweet_id_set)


class TweetFilterNotARetweet(TweetFilter):
    def filter(self, json_tweet_string):
        """
        Returns True if json_tweet_string is not a retweet
        """
        tweet = json.loads(json_tweet_string)

        if 'retweeted_status' in tweet:
            # Reject Tweets that the Twitter API considers to be retweets
            return False
        elif re.match(r'\s*RT\b', tweet['text']):
            # Reject Tweets that start with 'RT', even if not "officially" a retweet
            return False
        else:
            return True
        

class TweetFilterValidJSON(TweetFilter):
    def filter(self, json_tweet_string):
        """
        Returns True if json_tweet_string is a parsable JSON Tweet object
        """
        try:
            tweet = json.loads(json_tweet_string)
        except ValueError:
#            self._logger.warning("JSON Tweet object could not be parsed")
            return False
        else:
            if type(tweet) is dict:
                for tweet_field in ['id', 'id_str', 'text', 'user']:
                    if tweet_field not in tweet:
#                        self._logger.warning("JSON Tweet object did not have a '%s' field" % tweet_field)
                        return False
                if 'screen_name' not in tweet['user']:
                    return False
                return True
            else:
#                self._logger.warning("JSON Tweet object evalauted to a %s instead of a dict" % type(tweet))
                return False
