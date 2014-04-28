# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import fileinput
import json
import csv
import sys
import urllib
import urlparse
import time

class TopsyCrawler:
    """
    Crawl Topsy
    """
    API_KEY = ""
    base_url = "http://otter.topsy.com/search.json?q="
    base_params = {}
    csvHeadersWritten = False
    
    def __init__(self, api_key):
        self.API_KEY = api_key
    
    def queryBuilder(self, **kwargs):
        #Reference: http://stackoverflow.com/a/2506477/2762836
        """
        Builds complete query string to be used to query Topsy API
        Parameters:
        
        Window defines the time frame which is to be searched for tweets
        window=h (last 1 hour)
        window=d (last 1 day)
        window=d5 (last 5 days)
        window=w (last 7 days)
        window=m (last month)
        window=a (all time)
        
        """
        self.base_params = kwargs
        url_parts = list(urlparse.urlparse(self.base_url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(self.base_params)
        url_parts[4] = urllib.urlencode(query)
        initial_url = urlparse.urlunparse(url_parts)
        return initial_url
    
    def crawlUrl(self, url):
        """
        gets results from querying the url
        """
        return json.loads(urllib.urlopen(url).readlines()[0]) #return json output
    
    def fetchTweets(self, maxTweetNumber, delayPerRequest, **kwargs):
        """
        fetches tweets until the number of tweets fetched exceeds 'maxTweetNumber'
        'delayPerRequest' is the time in seconds to wait before making next request.
        """
        #Build first query
        url = self.queryBuilder(**kwargs)
        #First first page of results
        resultObj = {}
        resultObj = self.crawlUrl(url)
        processedResult = ResultsProcessor(resultObj)
        self.writeJsonToCsv(processedResult)
        self.csvHeadersWritten = True
        offset = processedResult.offset
        nextOffset = offset+10
        noOfTweetsFetched = len(processedResult.response['list'])
        while True:
            #Check if condition to exit the loop is met
            if noOfTweetsFetched > maxTweetNumber:
                break
            if len(processedResult.response['list']) == 0:
                break
            #Wait for sometime before next request
            time.sleep(delayPerRequest)
            #Query the url
            url = self.queryBuilder(apikey=self.base_params['apikey'], type=self.base_params['type'], window=self.base_params['window'], q=self.base_params['q'], offset=nextOffset)
            resultObj = self.crawlUrl(url)
            processedResult = ResultsProcessor(resultObj)
            self.writeJsonToCsv(processedResult)
            
            #Book keeping for processing next result
            nextOffset = nextOffset+10
            noOfTweetsFetched = len(processedResult.response['list']) + noOfTweetsFetched
            
    def writeJsonToCsv(self, jsonData):
        """
        Used to write tweets data to csv file
        """
        columnNames = []
        if self.csvHeadersWritten ==  False:
            #Write column names at the top of the csv
            columnNames  = ['hits','firstpost_date','title','url','trackback_date','trackback_total','url_expansions','target_birth_date','content',\
    'mytype','score','topsy_author_img','trackback_permalink','trackback_author_url','highlight','topsy_author_url','topsy_trackback_url','trackback_author_name','trackback_author_nick']
            print "\t".join(columnNames)
        
        #For now, simplify
        for tweet in jsonData.response['list']:
            line = ""
            for column in columnNames:
                if type(tweet[column])==unicode:
                    #print "string"
                    print tweet[column].encode('utf-8')+"\t"
                else:
                    #print "number"
                    print str(tweet[column])+"\t"
            
            
class ResultsProcessor:
    """
    This class will perform operations on json results received from Topsy Crawler class
    """
    resultsJsonDictionary = {}
    request = {}
    response = {}
    page = 0
    window = "" #specify if data is to be fetched from last day(d5), week(w), month(m) or all time(a)
    offset = 0
    hidden = 0
    total = 0
    last_offset = 0
    
    def __init__(self, resultsJson):
        self.resultsJsonDictionary = resultsJson #convert string into valid json format
        self.request = self.resultsJsonDictionary['request']
        self.response = self.resultsJsonDictionary['response']
        self.page = self.resultsJsonDictionary['response']['page']
        self.window = self.resultsJsonDictionary['response']['window']
        self.offset = self.resultsJsonDictionary['response']['offset']
        self.hidden = self.resultsJsonDictionary['response']['hidden']
        self.total = self.resultsJsonDictionary['response']['total']
        self.last_offset = self.resultsJsonDictionary['response']['last_offset']

# <codecell>

if __name__ == "__main__":
    API_KEY = "09C43A9B270A470B8EB8F2946A9369F3"
    """
    #Example to examine tweets
    crawlerObj = TopsyCrawler(API_KEY)
    url = crawlerObj.queryBuilder(apikey=API_KEY, type='tweet', window='a', q='#happy #surprised')
    jsonResults = crawlerObj.crawlUrl(url)
    resultsObj = ResultsProcessor(jsonResults)
    """
    #example to fetch multiple tweets
    crawlerObj = TopsyCrawler(API_KEY)
    crawlerObj.fetchTweets(50, 10, apikey=API_KEY, type='tweet', window='a', q='#happy #surprised')

