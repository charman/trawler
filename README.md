trawler
=======

Most of the interesting functionality is in the class
RateLimitedTwitterEndpoint. The class is a wrapper around the (Twython
wrapper around the) Twitter API that handles all of the details of
rate limiting.  It also robustly handles errors that occur when the
Twitter servers are temporarily misbehaving.

Once you've created an instance of RateLimitedTwitterEndpoint, call:

  endpoint.get_data(twitter_api_parameters)

and get_data() will return the data from the Twitter API as soon as
possible without violating the Twitter rate limits (and thus the
TOS). This means that get_data() may block for up to 15 minutes.  All
of the classes used by RateLimitedTwitterEndpoint are thread safe.
