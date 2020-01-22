import sqlite3 # DataBase library
import regex as re # regular expression library
import nltk # natural language toolkit
from nltk.stem import PorterStemmer # used for stemming the words
from nltk.corpus import stopwords # used for identifying and removing stop words
from ast import literal_eval # for converting string into tuple
import os # library for moving through directories
import webbrowser # library for opening web page into default browser

def SlicePositions(dict):
    for keys,values in dict.items():
        HitL = dict[keys]
        return HitL[4:] # this will slice and return list of all positions in the dictionary

def MultipleWordQuerry(querry_list):
    QuerryHitlist = {} # dictinary having hitlists of all words in querry
    RankedPage = {} # final dictionary having ranked page
    TempDict = {} # dictionary having docID as keys and word and its hitlist as nested dictionary
    SwappedDict = {} # dictionary having keys and values swapped
    prox_points = 0
    # code separating all those document having querry words
    for q in querry_list:
        conn = sqlite3.connect("E:\\STUDY\\LANGUAGES\\Projects\\Search Engine\\check\\invertedIndexdb.db") # creating database connection
        cur = conn.cursor() # creating cursor object
        cur.execute('''SELECT WordInfo FROM InvertedIndex WHERE Word=? ''',(q,))
        data = cur.fetchone()
        conn.commit()
        conn.close()
        data = list(data[0].split(','))
        for i in data:
            wordInfo = ''
            for j in range(len(i)):
                if i[j].isalnum() or i[j]=='-':
                    wordInfo += ''.join(i[j])
            wordInfo = wordInfo.split('-')
            if q in QuerryHitlist:
                QuerryHitlist[q].append(wordInfo)
            else:
                QuerryHitlist[q] = [wordInfo]
    # code preparing Ranked pages having docID's as keys and sum of points of all words in doc as values
    for keys,values in QuerryHitlist.items():
        for i in range(len(QuerryHitlist[keys])):
            points = 0
            l = QuerryHitlist[keys][i]
            # calculating points of single word
            if l[1] == 'T': # if word is in heading give 5 points
                points += 5
            if l[2] == 'T': # if word is in title give 7 points
                points += 7
            points += int(l[3]) # adding frequency of word to points
            if l[0] in RankedPage: # if docID already exit than word is of same doc add points with it
                RankedPage[l[0]] = int(RankedPage[l[0]]) + points
            else:
                RankedPage[l[0]] = points
    # code for preparing Temp dictionary
    for keys,values in QuerryHitlist.items():
        for i in range(len(QuerryHitlist[keys])):
            points = 0
            l = QuerryHitlist[keys][i]
            if l[0] in TempDict: # if docID already exit than word is of same doc add points with it
                TempDict[l[0]].append({keys:l})
            else:
                TempDict[l[0]] = [{keys:l}]
    # for final ranking the RankedPage 
    for keys,values in TempDict.items():
        prox_points = 0
        d = TempDict[keys]
        for i in range(len(d)):
            d1 = SlicePositions(d[i]) # here each d[i] is a dictionary
            for j in range(i+1,len(d)):
                d2 = SlicePositions(d[j])
                a = 0
                while(a < len(d1) and a < len(d2)):
                    prox_points = int((int(d1[a]) + int(d2[a])) / (int(d1[a]) - int(d2[a]))) * 10
                    a += 1
        if prox_points < 0: 
            prox_points *= (-1)
        RankedPage[keys] += prox_points 
    # code swapping dictionary keys and values to sort them in descending order
    for keys,values  in RankedPage.items():
        if values in SwappedDict:
            SwappedDict[values].append(keys)
        else:
            SwappedDict[RankedPage[keys]] = [keys]
    RankedPage = dict(sorted(SwappedDict.items(),reverse=True)) # sorting dictionary in descending order using keys
    return RankedPage

def SingleWordQuerry(querry):
    RankedPage = {} # dictionary having pages ranked
    conn = sqlite3.connect("E:\\STUDY\\LANGUAGES\\Projects\\Search Engine\\check\\invertedIndexdb.db") # creating database connection
    cur = conn.cursor() # creating cursor object
    cur.execute('''SELECT WordInfo FROM InvertedIndex WHERE Word=? ''',(querry[0],))
    data = cur.fetchone()
    conn.commit()
    conn.close()
    data = list(data[0].split(','))
    for i in data:
        wordInfo = ''
        points = 0
        for j in range(len(i)):
            if i[j].isalnum() or i[j]=='-':
                wordInfo += ''.join(i[j])
        wordInfo = wordInfo.split('-')
        # page ranking
        if wordInfo[1] == 'T': # if word is in heading give 5 points
            points += 5
        if wordInfo[2] == 'T': # if word is in title give 7 points
            points += 7
        points += int(wordInfo[3]) # adding frequency of word to points
        if points in RankedPage:
            RankedPage[points].append(wordInfo[0]) # at zero location we have document ID
        else:
            RankedPage[points] = [wordInfo[0]] # at zero location we have document ID
    RankedPage = dict(sorted(RankedPage.items(),reverse=True)) # sorting dictionary in descending order using keys
    return RankedPage

def Stemming(data):
    ps = PorterStemmer()
    StemmedData = list()
    for i in range(len(data)):
        StemmedData.append(ps.stem(data[i]))
    return StemmedData

def RemoveStopWords(data):
    stopWords = set(stopwords.words('english'))
    dataFilteresd = list()
    for w in data:
        if w not in stopWords and w.isalnum(): # removing stop and non-alphanumeric words
            dataFilteresd.append(w)
    return dataFilteresd

def RemoveMultipleWords(data):
    # instead of writing funtion for removing duplicates words comvert input string to set
     data = list(dict.fromkeys(data)) # coverting list to dictionary will automatically remove all duplicates
     return data     

if __name__=='__main__':
    PagesDict = {} # dictionary having ranked web pages
    count = 0
    check = False
    print('Search:',end='')
    search = input(str()) # taking input to search
    search = nltk.word_tokenize(search) # separating each word into tokens
    search = RemoveStopWords(search) # removing stop words
    # instead of writing funtion for removing duplicates words comvert input string to set
    if len(search) > 1:search = RemoveMultipleWords(search) # reducing similar words occurence to one
    search = Stemming(search) # stemming words
    if len(search) == 1:
        PagesDict = SingleWordQuerry(search)
    elif len(search) > 1:
        PagesDict = MultipleWordQuerry(search)
    # generating list of path of html files
    directory = 'E:\\STUDY\\LANGUAGES\\Projects\\Search Engine\\simple' # directory of html files
    htmlFiles_path = []
    for d,folders,files in os.walk(directory):
        for i in range(len(files)):
            if files[i].endswith('.html'):
                htmlFiles_path.append(d + '\\' + files[i])
    # opening the web pages
    if not len(PagesDict): # if pages dictionary is empty no result if found
        print('Sorry ! no result found :(')
    else:
        for keys,values in PagesDict.items():
            for i in PagesDict[keys]:
                webbrowser.open('file://' + htmlFiles_path[int(i)] )
                count += 1
                if count == 10:
                    check = True
            if check:
                break
