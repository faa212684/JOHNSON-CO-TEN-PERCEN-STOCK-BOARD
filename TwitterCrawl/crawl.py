# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

"""
Source: "Mining the Social Web, Second Edition by Matthew A. Russell"

#Things to do before using this file:
1) install twitter library using: 
    pip install twitter
2) Get an API key on Twitter by creating an app:
    a) Navigate to url: https://apps.twitter.com/
    b) Click on "Create New App"
    c) Fill in "Name" and "Description"
    d) In "Website" field , enter "http://example.com/"
    e) In Callback URL" field, enter "http://example.com/auth/twitter/callback/"
    f) Click on "Create your Twitter application"
    
3) Get Consumer key,secret and Oauth tokens:
    a) Navigate to url: https://apps.twitter.com/
    b) Click on your application name
    c) Find "API Keys" tab 
    d) "API key" is the "consumer key"
    e) "API secret" is the "consumer secret"
    f) Find "Your access token" tab
    g) Click on "Generate access token" button
    h) Click refresh on the webpage
    i) Now you will find "Access token" and "Access token secret" populated.
    j) "Access token" is OAUTH_TOKEN and "Access token secret" is OAUTH_TOKEN_SECRET
"""
import io
import sys
import time
from urllib2 import URLError
from httplib import BadStatusLine
import json
import twitter
from functools import partial
from sys import maxint
from functools import partial
from sys import maxint
def oauth_login():
# connect to twitter api
	CONSUMER_KEY = YOUR_CONSUMER_KEY
	CONSUMER_SECRET = YOUR_CONSUMER_SECRET
	OAUTH_TOKEN = YOUR_OAUTH_TOKEN
	OAUTH_TOKEN_SECRET = YOUR_OAUTH_TOKEN_SECRET
	auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
	CONSUMER_KEY, CONSUMER_SECRET)
	twitter_api = twitter.Twitter(auth=auth)
	return twitter_api

def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw): 

    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
    
        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e
    
        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429: 
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e
    
    wait_period = 2 
    error_count = 0 

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0 
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise

def twitter_search(twitter_api, q, max_results=200, **kw):
    search_results = twitter_api.search.tweets(q=q, count=100, **kw)
    statuses = search_results['statuses']
    
    # Enforce a reasonable limit
    max_results = min(1000, max_results)
    for _ in range(10): # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
            print search_results['search_metadata']['next_results']
        except KeyError, e: # No more results when next_results doesn't exist
            break
        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=')
                        for kv in next_results[1:].split("&") ])
        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']
        #if len(statuses) > max_results:
        #    break
    return statuses

if __name__=="__main__":
    twitter_api = oauth_login()	

    #Tags to search
    searchPhrase = "#happiness"
    maxNumberOfResults = 400
    results = twitter_search(twitter_api, q=searchPhrase, max_results=maxNumberOfResults)
    print "Number of results fetched: ",len(results)

