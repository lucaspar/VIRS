from cop.collection import Collection
from collections import deque

class Similarity:

    def sim(wd, wq):
        doc_length = len(wd)
        query_length = len(wq)
        
              
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

        sim = numerator / (sqrtDoc * sqrtQuery)
        return sim

    def calculate_rank(docs, docs_tfidf, query_w):
        rank = []
        for doc, tfidf in zip(docs, docs_tfidf):
            rank.append((sim(tfidf, query_w), doc))
        rank.sort()
        return rank