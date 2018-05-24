import os
import re
import nltk
from unicodedata import normalize

# Methods to process a collection of documents
class Collection(object):

    def __init__(self, collection_path):
        self.collection_path = collection_path
        self.file_list = self.getFileList()

        # Attempts to get stopwords
        try:
            nltk.data.find('corpora/stopwords')

        # Download stopwords
        except LookupError:
            NLTK_DATA_PATH = '/virs/.app_data/nltk_data'
            if not any(NLTK_DATA_PATH in p for p in nltk.data.path):
                nltk.data.path.append(NLTK_DATA_PATH)
            nltk.download('stopwords', download_dir=NLTK_DATA_PATH)

    # Get a file list from @path with extension @ext
    def getFileList(self, ext='txt'):
        files  = os.listdir(self.collection_path)
        texts = [_file for _file in files]
        return texts


    # Process content of @filepath returning its tokens
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
        for filename in self.file_list :
            wordlist = self.processTokens(self.collection_path + filename)
            for word in wordlist :
                tokens.append(word)
        return tokens
