from django.conf import settings

from cop.invertedIndex import InvertedIndex
from cop.ranking import Ranking
from collections import deque

import time
import math
import os

# Creates the Vector Space Model representation of a collection
class VectorSpaceModel(object):

    def __init__(self, collection_path):

        self.KAPPA = 0      # Double normalization for TFIDF calculation for DOCUMENTS
        self.ALPHA = 0    # Double normalization for TFIDF calculation for QUERY

        # set collection path
        self.collection_path = collection_path

        # set a reference to inverted index module
        self.ii = InvertedIndex(self.collection_path)
        self.file_list = self.ii.file_list
        self.corpus_size = len(self.file_list)

        # create the collection's postings list
        self.postings, self.friendly_filenames = self.ii.generatePostingsList()

    # Calculates the normalized term frequency given a tf and a maximum tf
    def normalized_tf(self, tf, max_tf):
        return self.KAPPA + (1.0-self.KAPPA) * tf / max_tf

    def generateVectorSpaceModel(self):

        '''
        RETURNED VALUE SCHEMA:
        vsm = {
            term1 {
                df:    df,
                idf:   idf,
                tf:    [ d1, d2, d3, ... ],
                tfidf: [ d1, d2, d3, ... ],
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

    def tfidf_calc(self, freq, max_freq, idf):
        return 0 if max_freq is 0 else (  ( self.ALPHA + ((1-self.ALPHA) * freq / max_freq) ) * idf  )

    # Processes a query on this object's collection
    # Returns a dictionary with the document ranking and other information
    def processQuery(self, query):

        # save query for processing
        filepath = os.path.join(settings.USER_QUERIES, str(time.time()))

        # make dir if it does not exist
        if not os.path.exists( filepath ):
            os.makedirs(filepath)

        # write query to file
        with open(os.path.join(filepath, "query"), "w", errors='replace') as file:
            file.write(str(query))

        # process tokens in saved query
        query_ii_obj = InvertedIndex(filepath)
        query_terms = query_ii_obj.generatePostingsList()[0]

        # process selected collection
        vsm_table = self.generateVectorSpaceModel()

        ffn = self.friendly_filenames                       # save friendly filenames relation
        wq = [0] * len(vsm_table)                           # query terms weights (TFIDFs)
        tfidfs = [[] for i in range(len(self.file_list))]   # documents terms weights (TFIDFs)
        terms = ['' for i in range(len(vsm_table))]         # terms list

        # calculate maximum frequency of a term in the query
        max_freq = 0
        for t in query_terms:
            max_freq = max(max_freq, query_terms[t][0][1])

        # calculate query weights (TFIDFs)
        for dn, doc in enumerate(self.file_list):
            for tn, t in enumerate(vsm_table):

                # copy term to list for output
                terms[tn] = t

                # calculate term's tfidf in query
                freq = query_terms[t][0][1] if t in query_terms else 0
                if freq > 0 and t in vsm_table:
                    wq[tn] = self.tfidf_calc(freq, max_freq, vsm_table[t]['idf'])
                else:
                    wq[tn] = 0

                # append to tfidfs
                tfidfs[dn].append(vsm_table[t]['tfidf'][dn])

        # with TFIDFs of docs and query (wq), calculate ranking
        sim = Ranking()
        ranking = sim.calculate_rank(self.file_list, tfidfs, wq)

        # build output dictionary
        outputs = {
            'ranking': ranking,
            'tfidfs': tfidfs,
            'terms': terms,
            'docs': self.file_list,
            'ffn': self.friendly_filenames,
            'wq': wq,
        }

        return outputs