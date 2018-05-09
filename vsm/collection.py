import os
import re
import nltk
from unicodedata import normalize

# Methods to process a collection of documents
class Collection(object):

    def __init__(self, collection_path):
        self.collection_path = collection_path
        self.filelist = self.getFileList()
        nltk.download('stopwords')  # download nltk data


    # Get a file list from @path with extension @ext
    def getFileList(self, ext='txt'):
        files  = os.listdir(self.collection_path)
        txts = [_file for _file in files if _file.endswith("." + ext)]
        return txts


    # Process content of @filepath
    def processTokens(self, filepath):

        # read file content
        with open(filepath, 'r') as _file:
            lines = _file.readlines()

        tokens = []
        for line in lines :
            line = line.lower()                     # lowercase
            words = re.findall(r"[\w']+", line)     # filter non-alphanumeric characters
            for word in words :
                # normalize by removing diacritics:
                word = normalize('NFKD', word).encode('ASCII', 'ignore').decode('ASCII')
                tokens.append(word)

        # remove stopwords
        stopwords_list = nltk.corpus.stopwords.words('portuguese')
        tokens = [x for x in tokens if x not in stopwords_list]

        return tokens


    # Load collection of documents given a file @path
    def loadCollection(self):
        tokens = []
        for filename in self.filelist :
            wordlist = self.processTokens(self.collection_path + filename)
            for word in wordlist :
                tokens.append(word)
        return tokens