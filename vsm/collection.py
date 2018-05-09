import os
import re
import nltk
from unicodedata import normalize

def getTXTsFromPath(path):
    files  = os.listdir(path)
    txts = [_file for _file in files if _file.lower().endswith(".txt")]
    return txts

def getTokensFor(path,txt):
    _file = open(path + txt, 'r')
    lines = _file.readlines()
    fileWords = []
    for line in lines :
        line = line.lower()
        words = re.findall(r"[\w']+", line)
        for word in words :
            word = normalize('NFKD', word).encode('ASCII', 'ignore').decode('ASCII')
            fileWords.append(word)
    _file.close()
    nltk.download('stopwords')
    stopwords_ = nltk.corpus.stopwords.words('portuguese')
    fileWords = [x for x in fileWords if x not in stopwords_]
    return fileWords

def getAllTokensFrom(path):
    tokens = []
    files = getTXTsFromPath(path)
    for _file in files :
        words = getTokensFor(path,_file)
        for word in words :
            tokens.append(word)
    return tokens