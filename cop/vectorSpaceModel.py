from cop.invertedIndex import InvertedIndex
from collections import deque
import math

# Creates the Vector Space Model representation of a collection
class VectorSpaceModel(object):

    def __init__(self, collection_path):

        self.K = 0      # Double normalization for TFIDF calculation

        # set collection path
        self.collection_path = collection_path

        # set a reference to inverted index module
        self.ii = InvertedIndex(self.collection_path)
        self.file_list = self.ii.file_list
        self.corpus_size = len(self.file_list)

        # create the collection's postings list
        self.postings = self.ii.generatePostingsList()

    # Calculates the normalized term frequency given a tf and a maximum tf
    def normalized_tf(self, tf, max_tf):
        return self.K + (1.0-self.K) * tf / max_tf

    def generateVectorSpaceModel(self):

        '''
        RETURNED VALUE SCHEMA:
        vsm = {
            term1 {
                df:    df,
                idf:   idf,
                tf:    [d1, d2, d3, ...],
                tfidf: [d1, d2, d3, ...],
            }
            term2 {
                df:    df,
                idf:   idf,
                tf:    [ d1, d2, d3, ... ],
                tfidf: [ d1, d2, d3, ... ],
            }
            # ...
        }
        '''

        vsm = {}
        file_indexes = {filename: counter for counter, filename in enumerate(self.file_list)}

        for filename in self.file_list :
            print(filename, file_indexes[filename])

        # calculate idf and frequencies for all terms
        for term, postings in self.postings.items():

            df = len(postings)

            # vector representation of a single term
            tvsm = {
                'tf':    [0] * self.corpus_size,
                'df':    df,
                'idf':   0,
                'tfidf': [0] * self.corpus_size,
            }

            # nothing is calculated if df is zero
            if (df == 0):
                vsm[term] = tvsm
                continue

            # create list of term frequencies
            tvsm['idf'] = math.log10(self.corpus_size / df)
            for doc, freq in postings:
                tvsm['tf'][file_indexes[doc]] = freq

            vsm[term] = tvsm

        # for each document, calculate its maximum term frequency
        max_tf = [0] * self.corpus_size
        for doc in range(0, self.corpus_size):
            fmax = 0
            for t in vsm:
                fmax = max(fmax, vsm[t]['tf'][doc])
            max_tf[doc] = fmax

        # for each term, calculate the tfidf for all documents
        for t in vsm:
            for doc_index, tf in enumerate(vsm[t]['tf']):
                ntf = self.normalized_tf(tf, max_tf[doc_index])
                vsm[t]['tfidf'][doc_index] = ntf * vsm[t]['idf']

        return vsm
