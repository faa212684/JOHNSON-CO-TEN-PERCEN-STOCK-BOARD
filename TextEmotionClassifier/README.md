We try to classify each song by finding each songs representation in each of the mood category.

Example usage:
==============
Dislpay options using help 
----------------------------
python ../moodClassifier.py -h  

This classifier returns 2 dictionaries, first one gives number of words belonging to each mood category in input text  
The second dictionary gives every word belonging to each mood in input text  
Usage:  ../moodClassifier.py  
    -h --help           : displays help  
    -l --emotionlexicon : text file containing emotion words  
    -t --inputtext      : input text which is to be classified in different mood categorized  
    -f --textfile       : input file containing text for which mood categories are to found  
    Note: Don't use -t and -f flags simultaneously. In other words, either use text in command line argument or enter the file name, but not both  


Find mood categories of input text file and write output in csv text format to a file:  
--------------------------------------------------------------------------------------  
python ../moodClassifier.py -o -l ../EmotionLexicon/NRCEmotionLexicon.txt -f ../examples/sample.txt > ../examples/fileCSVOutput.txt  

Writing output dictionaries to console:  
--------------------------------------
python ../moodClassifier.py -l ../EmotionLexicon/NRCEmotionLexicon.txt -f ../examples/sample.txt > ../examples/consoleOutput.txt  

Using MoodClassifier in code:  
----------------------------  
from moodClassifier import MoodClassifier():  
text = "some random input text, type whatever you like here"  
obj = MoodClassifier(emotionLexiconFileName)  
dictMoodDistribution, dictMoodWords = obj.findMoodDistribution(text)  
print dictMoodDistribution  
print dictMoodWords  
