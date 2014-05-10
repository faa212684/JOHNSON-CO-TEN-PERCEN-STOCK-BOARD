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
        print initial_url
        sys.stdout.flush()
        return initial_url
    
    def crawlUrl(self, url):
        """
        gets results from querying the url
        """
        return json.loads(urllib.urlopen(url).readlines()[0]) #return json output
    
    def fetchTweets(self, maxTweetNumber, delayPerRequest, writeFileHandle, folderName, **kwargs):
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
        self.writeJsonToCsv(processedResult, resultObj, writeFileHandle, 0, kwargs['q'], folderName)
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
            self.writeJsonToCsv(processedResult, resultObj, writeFileHandle, nextOffset, kwargs['q'], folderName)
            
            #Book keeping for processing next result
            nextOffset = nextOffset+10
            noOfTweetsFetched = len(processedResult.response['list']) + noOfTweetsFetched
            #print "noOfTweetsFetched: ",noOfTweetsFetched
            
    def writeJsonToCsv(self, jsonData, jsonRawData, writeFile, offset, queryTags, folderName):
        """
        Used to write tweets data to csv file
        writeFileHandle is False if output is to be written to stdout
        writeFileHandle has fileName if output json is to be written to file
        """
        if not writeFile:
            columnNames  = ['hits','firstpost_date','title','url','trackback_date','trackback_total','url_expansions','target_birth_date','content',\
        'mytype','score','topsy_author_img','trackback_permalink','trackback_author_url','highlight','topsy_author_url','topsy_trackback_url','trackback_author_name','trackback_author_nick']
            if self.csvHeadersWritten ==  False:
                #Write column names at the top of the csv
                print "\t".join(columnNames)
            
            #For now, simplify
            for tweet in jsonData.response['list']:
                line = ""
                for column in columnNames:
                    if type(tweet[column])==unicode:
                        #print "string"
                        if column == 'trackback_author_nick':
                            #This is the last column and so insert new line after it for the new tweet
                            print repr(tweet[column].encode('utf-8'))+"\t"
                        else:
                            print repr(tweet[column].encode('utf-8'))+"\t",
                    else:
                        #print "number"
                        print str(tweet[column])+"\t",
        else:
            #write json output to file
            myfp = open(folderName+"/"+"_".join(queryTags.lower().split())+"_"+ str(offset) +".json","w")
            json.dump(jsonRawData,  myfp, indent=4, sort_keys=False, separators=(',', ': '))
            myfp.close()
        
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
    
    try:
        no_of_results = int(sys.argv[1])
        time_delay = float(sys.argv[2])
        if sys.argv[3] == "True" or sys.argv[3] == "true":
            write_to_file_flag = True
        else:
            write_to_file_flag = False
        path_to_store_results = sys.argv[4]
        query = sys.argv[5]                    
        
        print no_of_results
        print time_delay
        print write_to_file_flag
        print path_to_store_results
        print query
        
        crawlerObj.fetchTweets(no_of_results, time_delay, write_to_file_flag, path_to_store_results, apikey=API_KEY, type='tweet', window='a', q=query)
    except:
        print "Usage: python scriptName no_of_tweets_to_fetch time_delay_between_queries write_to_file_flag path_to_store_results query"
        print "Error: ",sys.exc_info()[1]

