from nltk.stem import PorterStemmer # used for stemming the words
from nltk.corpus import stopwords # used for identifying and removing stop words
from bs4 import BeautifulSoup # web-crawler
from ast import literal_eval # for converting string into tuple
import sqlite3 # DataBase library
import nltk # natural language toolkit
import time # to note running time of program
import os # library for moving through directories
import re # used for extrating headings from html page

def Stemming(tempDict, data):
    # func for steming the words e.g simplified and simpler into simpl
    # also func for calculating frequency and positions of words in html document
    ps = PorterStemmer()
    StemmedData = list()
    for i in range(len(data)):
        StemmedData.append(ps.stem(data[i]))
        # calculating frequency and postions of words in html document
        if StemmedData[-1] in tempDict:
            tempDict[StemmedData[-1]][0] += 1
            tempDict[StemmedData[-1]].append(i) # over writing new info
        else:
            tempDict[StemmedData[-1]] = [1, i]
    return StemmedData

def RemoveStopWords(data):
    # func for removing stopwords from html data e.g i,me,my,myself,we,our,how,about etc
    stopWords = list(stopwords.words('english'))
    dataFilteresd = list()
    for w in data:
        if w not in stopWords and w.isalnum(): # removing stop and non-alphanumeric words
            dataFilteresd.append(w)
    return dataFilteresd # list with removed stopwords

def Slicer(data):
    # this func removes the irrelevant text from html Documents
    # i.e starts from Welcome to Simple and from end 'Views' heading
    start = data.find('From the Simple English Wikipedia')
    end = data.rfind('Views')
    doc1 = data[start+32:end]
    return doc1

def docInfo(Hash_table, path,DocID):
    tempDict = {}
    with open(path , encoding = 'ISO-8859-1') as f:
        soup = BeautifulSoup(f.read(),"lxml") # BeautifulSoup object for extracting info from html document
    stem_obj = PorterStemmer() # stemmer obj for stemming headings and title
    # code for checking headings and stemming them
    headings = str()
    for heading in soup.find_all(re.compile('^h[1-6]$')):
        headings = headings + ' ' + (heading.text.strip())
    headings = nltk.word_tokenize(headings)
    stemmedHeadings = list()
    for h in headings:
        stemmedHeadings.append(stem_obj.stem(h))
    #  code for checking title and stemming it
    stemmedTitle = list()
    try: # exception handling for non-alphanumeric characters in title
        Title = nltk.word_tokenize(soup.title.text) # tokenizing title
        for t in Title:
            stemmedTitle.append(stem_obj.stem(t)) # converting title words into stem words
    except:
        pass
    # code for slicing, nokenizing, removing stop-words and stemming word of html document
    doc = soup.get_text() # gives all text of html file
    doc = Slicer(doc) # func call
    doc = nltk.word_tokenize(doc) # separating each word into tokens
    doc = RemoveStopWords(doc) # func call
    doc = Stemming(tempDict, doc) # func call
    # code for other parameters i.e isHeading,isTitle
    for w in tempDict:
        isHeading = 'F'
        isTitle = 'F'
        # checking if word appear as a heading
        for h in stemmedHeadings:
            if w in h:
                isHeading = 'T'
                break
        # checking if word appear as a title
        if w in stemmedTitle:
            isTitle = 'T'
        s = map(str,tempDict[w]) # s is list of word frequency and positions
        s = '-'.join(s) # converting map items to string
        word_info = str(DocID) + '-' + isHeading + '-' + isTitle + '-' + s
        # code for adding word and its info in Hash Table dictionary
        if w in Hash_table: # if word already exists then updating that row with new docID and wordInfo
            # this will give last inserted value in a key to compare its docID
            t = Hash_table[w][-1]
            ID = t[0]
            if ID != DocID:
                Hash_table[w].append(word_info)
        else:
            Hash_table[w] = [word_info] # inserting key and its values in dictionary

def Parser_func(directory):
    Hash_table = {} # dictionary for words as keys and word_info as values
    DocID = 0 # document Id of each word
    check = False
    conn = sqlite3.connect("E:\\STUDY\\LANGUAGES\\Projects\\Search Engine\\check\\invertedIndexdb.db") # creating database connection
    cur = conn.cursor() # creating cursor object
    cur.execute('''CREATE TABLE InvertedIndex(Word string,WordInfo string)''')
    for d,folders,files in os.walk(directory): # moving in directories to find html file
        for i in range(len(files)):
            if files[i].endswith('.html'): # check whether file is html
                html_path = str(d + '\\' + files[i])
                print('parsing file # {}'.format(DocID))
                docInfo(Hash_table, html_path, DocID)
                DocID += 1
                if DocID == 1000:
                    check = True
                    break
        if check:
            break
    for key,values in Hash_table.items(): # inserting in dataBase from Hash_table dictionary
        cur.execute('''INSERT INTO InvertedIndex(Word,WordInfo)VALUES(?,?)''',(key,str(values)))
    conn.commit()
    conn.close()

if __name__=='__main__':
    start_time = time.time() # time class for getting current time
    directory = 'E:\\STUDY\\LANGUAGES\\Projects\\Search Engine\\simple' # directory of html files total html files = 109833
    Parser_func(directory) # funtion for moving in directory and finding html files for parsing
    minutes = int((time.time() - start_time) / 60) # time in minutes
    seconds = int((time.time() - start_time) % 60) # time in seconds
    print('Time Taken : {} minutes, {} seconds'.format(minutes,seconds)) # printing total time taken
