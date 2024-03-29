import os # library for moving through directories
import sqlite3 # DataBase library
import nltk # natural language toolkit
import re # used for extrating headings from html page
from nltk.corpus import stopwords # used for identifying and removing stop words
from nltk.stem import PorterStemmer # used for stemming the words
from bs4 import BeautifulSoup # web-crawler
import time

def Stemming(data):
    # func for steming the words in html data e.g simplified and simpler into simpl
    ps = PorterStemmer()
    StemmedData = list()
    for i in range(len(data)):
        StemmedData.append(ps.stem(data[i]))
    return StemmedData

def RemoveStopWords(data):
    # func for removing stopwords from html data e.g i,me,my,myself,we,our etc
    stopWords = set(stopwords.words('english'))
    dataFilteresd = list()
    for w in data:
        if w not in stopWords:
            dataFilteresd.append(w)
    return dataFilteresd # list with removed stopwords

def Slicer(data):
    # this func removes the irrelevant text from html Documents
    # i.e starts from Welcome to Simple and from end 'Views' heading
    start = data.find('From the Simple English Wikipedia')
    end = data.rfind('Views')
    doc1 = data[start:end]
    return doc1

def docInfo(path, Hash_table, DocID):
    with open(path , encoding = 'ISO-8859-1') as f:
        soup = BeautifulSoup(f.read(),"lxml")
        #code for checking headings
        headings = []
        for heading in soup.find_all(re.compile('^h[1-6]$')):
            headings.append(heading.text.strip())
        doc = soup.get_text() # gives all text of html file
        doc = Slicer(doc) # func call
        doc = nltk.word_tokenize(doc) # separating each word into tokens
        doc = RemoveStopWords(doc) # func call
        doc = Stemming(doc) # func call
        #code for other parameters i.e frequency,isHeading,isTitle,position
        for j in range(len(doc)):
            frequency = 0
            isHeading = 'F'
            isTitle = 'F'
            word = doc[j]
            position = str('')
            #calculating frequency and position of a word
            for k in range(j,len(doc)):
                if doc[k] == doc[j]:
                    frequency += 1
                    position = position + str(k) + ','
            # checking if word appear as a heading
            for i in headings:
                if doc[j] in i:
                    isHeading = 'T'
                    break
            # checking if word appear as a title
            if doc[j] in soup.title.text:
                isTitle = 'T'
            word_info = str(str(DocID) + ',' + str(frequency) + ',' + isHeading + ',' + isTitle + '+' + str(position))
            #code for adding word and its info in Hash Table
            if word not in Hash_table: # checking if key already exists in dictionary or not
                Hash_table[word] = word_info # inserting key and its values in dictionary

def Parser_func(direct):
    Hash_table = {}
    #creating database connection
    #conn = sqlite3.connect("E:\\STUDY\\LANGUAGES\\Projects\\Search Engine\\check\\forwardIndexdb.db")
    #cur = conn.cursor()
    #cur.execute('''CREATE TABLE ForwardIndex(Word string,Word_info string)''')
    check = False
    docID = 0
    for d,folders,files in os.walk(direct):
        # check whether file is html
        for i in range(len(files)):
            if files[i].endswith('.html'):
                print('parsing file {}'.format(docID))
                path_Of_html_file = str(d + '\\' + files[i])
                docInfo(path_Of_html_file, Hash_table, docID)
                docID += 1
            if docID == 1000:
                check = True
                break
        if check:
            break
    #for keys,values in Hash_table.items(): # making forward_index from dictionary
        #cur.execute('''INSERT INTO ForwardIndex(Word,Word_info)VALUES(?,?)''',(keys,values))
    #conn.commit()
    #conn.close()

def main():
    directory = 'E:\\STUDY\\LANGUAGES\\Projects\\Search Engine\\simple'
    # total html files = 109833
    Parser_func(directory) # func call

if __name__=='__main__':
    start_time = time.time()
    main()
    minutes = int((time.time() - start_time) / 60) # time taken in minutes
    seconds = int((time.time() - start_time) % 60) # time taken in seconds
    print('Time Taken : {} minutes, {} seconds'.format(minutes,seconds))
