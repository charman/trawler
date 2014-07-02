#!/usr/bin/env python

"""
"""

# Standard Library modules
import unittest

# Local modules
from tweet_filter import *


class TestFilterValidJSON(unittest.TestCase):
    def test_check_required_fields(self):
        json_tweet = '{"id": 1, "id_str": "1", "text":"foo", "user": {"screen_name": "charman"}}'
        json_tweet_no_screen_name = '{"id": 1, "id_str": "1", "text":"foo"}'
        tweet_json_filter = TweetFilterValidJSON()

        self.assertTrue(tweet_json_filter.filter(json_tweet))
        self.assertFalse(tweet_json_filter.filter(json_tweet_no_screen_name))


class TestFilterNoURLs(unittest.TestCase):
    def test_url_filtering(self):
        json_tweet_http = '{"id": 1, "id_str": "1", "text":"http://twitter.com"}'
        json_tweet_https = '{"id": 2, "id_str": "2", "text":"https://twitter.com"}'
        json_tweet_clean = '{"id": 3, "id_str": "3", "text":"no urls here"}'
        tweet_no_url_filter = TweetFilterNoURLs()

        self.assertFalse(tweet_no_url_filter.filter(json_tweet_http))
        self.assertFalse(tweet_no_url_filter.filter(json_tweet_https))
        self.assertTrue(tweet_no_url_filter.filter(json_tweet_clean))


class TestFilterOneTweetPerScreenName(unittest.TestCase):
    def test_screen_name_filtering(self):
        json_tweet_1 = '{"id": 1, "id_str": "1", "user": {"screen_name":"charman"}}'
        json_tweet_2 = '{"id": 2, "id_str": "2", "user": {"screen_name":"PHonyDoc"}}'
        json_tweet_3 = '{"id": 3, "id_str": "3", "user": {"screen_name":"charman"}}'
        json_tweet_4 = '{"id": 4, "id_str": "4", "user": {"screen_name":"PHonyDoc"}}'
        screen_name_filter = TweetFilterOneTweetPerScreenName(TweetFilter)

        self.assertTrue(screen_name_filter.filter(json_tweet_1))
        self.assertTrue(screen_name_filter.filter(json_tweet_2))
        self.assertFalse(screen_name_filter.filter(json_tweet_3))
        self.assertFalse(screen_name_filter.filter(json_tweet_4))


class TestFilterReliablyEnglish(unittest.TestCase):
    def test_english_filtering(self):
        spanish_tweet = '{"id": 1, "id_str": "1", "text":"Muchas de las victimas fueron mostrados con vendajes aplicados a toda prisa"}'
        english_tweet = '{"id": 2, "id_str": "2", "text":"The quick brown fox jumped over the lazy sleeping dog"}'
        english_filter = TweetFilterReliablyEnglish()

        self.assertFalse(english_filter.filter(spanish_tweet))
        self.assertTrue(english_filter.filter(english_tweet))


class TestFilterTweetIDInSet(unittest.TestCase):
    def test_add_tweet_functions(self):
        json_tweet_1 = '{"id": 1, "id_str": "1"}'
        json_tweet_2 = '{"id": 2, "id_str": "2"}'
        json_tweet_3 = '{"id": 3, "id_str": "3"}'
        json_tweet_4 = '{"id": 4, "id_str": "4"}'
        json_tweet_5 = '{"id": 5, "id_str": "5"}'
        tweet_id_filter = TweetFilterTweetIDInSet()

        self.assertFalse(tweet_id_filter.filter(json_tweet_1))
        tweet_id_filter.add_tweet(json_tweet_1)
        self.assertTrue(tweet_id_filter.filter(json_tweet_1))

        tweet_id_filter.add_tweets([json_tweet_2, json_tweet_3])
        self.assertTrue(tweet_id_filter.filter(json_tweet_2))
        self.assertTrue(tweet_id_filter.filter(json_tweet_3))

        self.assertFalse(tweet_id_filter.filter(json_tweet_4))
        tweet_id_filter.add_tweet_id(4)
        self.assertTrue(tweet_id_filter.filter(json_tweet_4))

        tweet_id_filter.add_tweet_ids([4,5])
        self.assertTrue(tweet_id_filter.filter(json_tweet_5))

    def test_tweet_id_as_ints(self):
        json_tweet_1 = '{"id": 1, "id_str": "1"}'
        tweet_id_filter = TweetFilterTweetIDInSet()
        self.assertFalse(tweet_id_filter.filter(json_tweet_1))
        tweet_id_filter.add_tweet_id(1)
        self.assertTrue(tweet_id_filter.filter(json_tweet_1))

    def test_tweet_id_as_unicode(self):
        json_tweet_1 = '{"id": 1, "id_str": "1"}'
        tweet_id_filter = TweetFilterTweetIDInSet()
        self.assertFalse(tweet_id_filter.filter(json_tweet_1))
        tweet_id_filter.add_tweet_id(u'1')
        self.assertTrue(tweet_id_filter.filter(json_tweet_1))



class TestFilterTweetIDNotInSet(unittest.TestCase):
    def test_add_tweet_functions(self):
        json_tweet_1 = '{"id": 1, "id_str": "1"}'
        json_tweet_2 = '{"id": 2, "id_str": "2"}'
        json_tweet_3 = '{"id": 3, "id_str": "3"}'
        json_tweet_4 = '{"id": 4, "id_str": "4"}'
        json_tweet_5 = '{"id": 5, "id_str": "5"}'
        tweet_id_filter = TweetFilterTweetIDNotInSet()

        self.assertTrue(tweet_id_filter.filter(json_tweet_1))
        tweet_id_filter.add_tweet(json_tweet_1)
        self.assertFalse(tweet_id_filter.filter(json_tweet_1))

        tweet_id_filter.add_tweets([json_tweet_2, json_tweet_3])
        self.assertFalse(tweet_id_filter.filter(json_tweet_2))
        self.assertFalse(tweet_id_filter.filter(json_tweet_3))

        self.assertTrue(tweet_id_filter.filter(json_tweet_4))
        tweet_id_filter.add_tweet_id(4)
        self.assertFalse(tweet_id_filter.filter(json_tweet_4))

        tweet_id_filter.add_tweet_ids([4,5])
        self.assertFalse(tweet_id_filter.filter(json_tweet_5))

    def test_tweet_id_as_ints(self):
        json_tweet_1 = '{"id": 1, "id_str": "1"}'
        tweet_id_filter = TweetFilterTweetIDNotInSet()
        self.assertTrue(tweet_id_filter.filter(json_tweet_1))
        tweet_id_filter.add_tweet_id(1)
        self.assertFalse(tweet_id_filter.filter(json_tweet_1))

    def test_tweet_id_as_unicode(self):
        json_tweet_1 = '{"id": 1, "id_str": "1"}'
        tweet_id_filter = TweetFilterTweetIDNotInSet()
        self.assertTrue(tweet_id_filter.filter(json_tweet_1))
        tweet_id_filter.add_tweet_id(u'1')
        self.assertFalse(tweet_id_filter.filter(json_tweet_1))



class TestFilteredTweetReader(unittest.TestCase):
    def test_add_filter_when_reader_crated(self):
        filtered_reader = FilteredTweetReader([TweetFilterNotARetweet()])
        filtered_reader.open("testdata/shears.txt")
        self.assertEqual(total_tweets_passed_through_filters(filtered_reader), 30)
        filtered_reader.close()

    def test_add_multiple_filters(self):
        filtered_reader = FilteredTweetReader()
        filtered_reader.add_filter(TweetFilterNotARetweet())
        filtered_reader.add_filter(TweetFilterFieldMatchesRegEx('text', r'\bmy %s(s|es)?\b' % 'shears'))
        filtered_reader.open("testdata/shears.txt")
        self.assertEqual(total_tweets_passed_through_filters(filtered_reader), 19)
        filtered_reader.close()

    def test_filter_field_matches_regex(self):
        filtered_reader = FilteredTweetReader()
        regex_filter = TweetFilterFieldMatchesRegEx('text', r'\bmy %s(s|es)?\b' % 'shears')
        filtered_reader.add_filter(regex_filter)
        filtered_reader.open("testdata/shears.txt")
        self.assertEqual(total_tweets_passed_through_filters(filtered_reader), 20)
        filtered_reader.close()

    def test_filter_not_a_retweet(self):
        filtered_reader = FilteredTweetReader()
        filtered_reader.add_filter(TweetFilterNotARetweet())

        filtered_reader.open("testdata/retweet_x1")
        self.assertEqual(total_tweets_passed_through_filters(filtered_reader), 0)
        filtered_reader.close()

        filtered_reader.open("testdata/shears.txt")
        self.assertEqual(total_tweets_passed_through_filters(filtered_reader), 30)
        filtered_reader.close()

    def test_filter_valid_json(self):
        # FilteredTweetReader() uses the valid JSON filter by default
        filtered_reader = FilteredTweetReader()
        filtered_reader.open("testdata/bad_json_tweets_x3")
        self.assertEqual(total_tweets_passed_through_filters(filtered_reader), 0)
        filtered_reader.close()

    def test_reader_with_no_filters(self):
        filtered_reader = FilteredTweetReader()
        filtered_reader.open("testdata/shears.txt")
        self.assertEqual(total_tweets_passed_through_filters(filtered_reader), 32)
        filtered_reader.close()

    def test_filter_raises_exception(self):
        filtered_reader = FilteredTweetReader()
        filtered_reader.add_filter(TweetFilterAlwaysRaiseException())

        filtered_reader.open("testdata/shears.txt")
        self.assertRaises(Exception, total_tweets_passed_through_filters, filtered_reader)
        filtered_reader.close()

    def test_filters_short_circuit_after_first_rejection(self):
        filtered_reader = FilteredTweetReader()
        # Filteres are applied in order, so TweetFilterAlwaysRaiseException should never be called
        filtered_reader.add_filter(TweetFilterAlwaysReject())
        filtered_reader.add_filter(TweetFilterAlwaysRaiseException())

        filtered_reader.open("testdata/shears.txt")
        self.assertEqual(total_tweets_passed_through_filters(filtered_reader), 0)
        filtered_reader.close()


def total_tweets_passed_through_filters(filtered_reader):
    tweets = []
    for tweet in filtered_reader:
        tweets.append(tweet)
    return len(tweets)


class TweetFilterAlwaysRaiseException(TweetFilter):
    def filter(self, json_tweet_string):
        raise Exception


class TweetFilterAlwaysReject(TweetFilter):
    def filter(self, json_tweet_string):
        return False



if __name__ == '__main__':
    unittest.main(buffer=True)
