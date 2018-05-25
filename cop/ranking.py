from cop.collection import Collection
from collections import deque
import math

# Similarities and ranking computation
class Ranking:

    # computes the cosine similarity between weights (TFIDFs) of a document and a query
    def sim(self, wd, wq):

        doc_length = len(wd)
        query_length = len(wq)
        assert doc_length == query_length

        numerator = 0
        for i in range(0, doc_length):
            numerator += wd[i]*wq[i]

        sqrtDoc = 0
        for i in range(0, doc_length):
            sqrtDoc += wd[i]**2
        sqrtDoc = math.sqrt(sqrtDoc)

        sqrtQuery = 0
        for i in range(0, query_length):
            sqrtQuery += wq[i]**2
        sqrtQuery = math.sqrt(sqrtQuery)

        denominator = (sqrtDoc * sqrtQuery)
        sim = numerator / denominator if denominator != 0 else 0

        return sim

    # computes similarities and sort documents for ranking
    def calculate_rank(self, docs, docs_tfidf, query_w):
        rank = []
        for doc, tfidf in zip(docs, docs_tfidf):
            similarity = self.sim(tfidf, query_w)
            rank.append((similarity, doc))
        rank.sort(reverse=True)
        return rank
