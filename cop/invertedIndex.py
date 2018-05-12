from cop.collection import Collection
from collections import deque

class InvertedIndex(object):

    def __init__(self, collection_path):

        # set collection path
        self.collection_path = collection_path

        # set a reference to collection processing module
        self.cc = Collection(self.collection_path)


    # count word frequencies given a @filename
    def countTokens (self, filename):

        words = []
        frequencies = {}

        # extract tokens from file
        tokens = self.cc.processTokens(self.collection_path + filename)

        for token in tokens:

            # increment token frequency
            if token not in frequencies:
                frequencies[token] = 1
            else:
                frequencies[token] += 1

        return frequencies


    # craft postings list
    def collectionPostingsList (self):
        postings = {}
        files = self.cc.getFileList()

        for _file in files:

            # count term frequencies for file
            terms_frequencies = self.countTokens(_file)

            for t,f in terms_frequencies.items():

                # append frequency to term posting list
                if t not in postings:
                    postings[t] = deque([])
                postings[t].append((_file, f))

        return postings
