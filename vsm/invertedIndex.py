from vsm.collection import Collection
from collections import deque

class InvertedIndex(object):

    def __init__(self, collection_path):
        self.collection_path = collection_path
        self.cc = Collection(self.collection_path)

    def countTokens (self, filename):
        words = []
        frequences = []
        tokens = self.cc.processTokens(self.collection_path + filename)
        for token in tokens:
            if token not in  words:
                words.append(token)
                frequences.append(1)
            else:
                frequences[words.index(token)]+=1    
        return words, frequences


    def collectionCountTokens (self):
        tokens = {}
        files = self.cc.getFileList()
        for _file in files:
            words, frequences = self.countTokens(_file)
            for word in words:
                filefrequence = (_file,frequences[words.index(word)])
                if word not in tokens:
                    tokens[word] = deque([])
                tokens[word].append(filefrequence)
        print (tokens)
        return tokens
        