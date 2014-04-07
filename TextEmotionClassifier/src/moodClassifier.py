#!/usr/bin/python
#title                  :moodClassifier.py
#description            :Classify text in ten different emotions
#author                 :Nakul Dhande
#date                   :20140407
#version                :0.1
#==============================================================================

import sys
import pickle
import re
import getopt

class MoodClassifier:
    dictWordMoods = {} #has list of moods for each word, words without any mood have empty list
    pattern=re.compile("[^\w']")
    
    
    def __init__(self, emotionLexiconFileName):
        #Initialize the dictWordMoods 
        self.dictWordMoods = self.initializeDictWordMoods(emotionLexiconFileName)
    	
    	
    def findMoodDistribution(self, text):
        #Find mood distribution for input text
        moods = "anger anticipation disgust fear joy negative positive sadness surprise trust"
        # 1. Clean text first, remove all special characters, make them lowercase
        cleanedText = self.cleanText(text)
        # 2. Find each of these words in emotion lexicon dictionary and prepare a new dictionary:
        # {emotion:countOfWords}
        dictMoodDistribution = {}
        #initialize each mood's count to zero
        for mood in moods.split():
            dictMoodDistribution[mood] = 0
        #Dictionary to keep track of words in each of the mood category
        dictMoodWords = {}
        #eight moods: negative, anger, fear, sadness, anticipation, trust, positive, disgust, joy, surprise
        for word in cleanedText.split():
            #for each word in input text
            if word in self.dictWordMoods:
                #check if word is available in Emotion lexicon with it's representative moods
                listOfMoods = self.dictWordMoods[word]
                for mood in listOfMoods:
                    #Get all the moods which the words represents
                    if mood in dictMoodDistribution:
                        #Increase count of mood category
                        dictMoodDistribution[mood] += 1
                    #Add word to mood list to find which words in which mood are present in song
                    if mood in dictMoodWords:
                        dictMoodWords[mood].append(word)
                    else:
                        dictMoodWords[mood] = [word]
        return dictMoodDistribution, dictMoodWords


    def readFileLineByLine(self, emotionLexiconFileName):
        #generator for reading file line by line
        for line in open(emotionLexiconFileName,"r"):
            yield line

    
    def initializeDictWordMoods(self, emotionLexiconFileName):
        #Read emotionLexiconFile line by line and prepare dictionary
        dictWordMoods = {}
        for line in self.readFileLineByLine(emotionLexiconFileName):
            cleanLine = line.replace("\r"," ").replace("\n"," ").strip()
            tokens = cleanLine.split()
            #first word is the word and rest of the words are moods
            if len(tokens) > 1:
                dictWordMoods[tokens[0]] = tokens[1:]
            #Don't include those words which don't have their moods classified
        return dictWordMoods
		
		
    def cleanText(self, inputText):
        """
        returns lower case input_text and removes special characters except underscore and apostrophe.
        """
        cleanPhrases = inputText.lower()
        cleanPhrases = self.pattern.sub(' ', cleanPhrases)
        return cleanPhrases
     
        
def usage():
    print "Usage: ",sys.argv[0],"\n\
    -h --help           : displays help\n\
    -l --emotionlexicon : text file containing emotion words\n\
    -t --inputtext      : input text which is to be classified in different mood categorized\n\
    -f --textfile       : input file containing text for which mood categories are to found\n\
    Note: Don't use -t and -f flags simultaneously. In other words, either use text in command line argument or enter the file name, but not both"
     
def main():
    if len(sys.argv) == 1:
        usage()
        sys.exit(0)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:t:f:o", ["help", "emotionlexicon=", "inputtext=","textfile=","outputCSV="])
    except getopt.GetoptError as err:
        # print help information and exit:
        #print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    except:
        usage()
    
    emotionLexiconFileName = ""
    verbose = ""
    inputText = ""
    inputTextFileName = ""
    outputCSV = False
    
    #print args
    #print opts
    
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            print "This classifier returns 2 dictionaries, first one gives number of words belonging to each mood category in input text\nThe second dictionary gives every word belonging to each mood in input text"
            usage()
            sys.exit(0)
        elif o in ("-l", "--emotionlexicon"):
            emotionLexiconFileName = a
        elif o in ("-t","--inputtext"):
            inputText = a
        elif o in ("-f","--textfile"):
            inputTextFileName = a
        elif o in ("-o","--outputCSV"):
            outputCSV = True
        else:
            assert False, "unhandled option"
    
    #Get mood for input text
    text = ""
    if inputTextFileName != "":
        #Read text from file
        text = " ".join(open(inputTextFileName,"r").readlines())
    elif inputText != "":
        #Read text directly
        text = inputText 
    obj = MoodClassifier(emotionLexiconFileName)
    dictMoodDistribution, dictMoodWords = obj.findMoodDistribution(text)
    if outputCSV:
        #return output in csv format 
        moods = "anger anticipation disgust fear joy negative positive sadness surprise trust"
        return emotionLexiconFileName+"\t"+"\t".join( str(dictMoodDistribution[x]) for x in moods.split())+"\n"
    else:
        return (dictMoodDistribution, dictMoodWords)
    
if __name__=="__main__":
    print main()
