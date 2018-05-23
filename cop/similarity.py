from cop.collection import Collection
from collections import deque

class Similarity:

    def sim(wd, wq):
        tamDoc = len(wd)
        tamQuery = len(wq)
        
              
        numerator = 0
        for i in range(1, tamDoc):
            numerator += wd[i]*wq[i]
        
        sqrtDoc = 0
        for i in range(1, tamDoc):
            sqrtDoc += wd[i]**2
        sqrtDoc = math.sqrt(sqrtDoc)

        sqrtQuery = 0
        for i in range(1, tamQuery):
            sqrtQuery += wq[i]**2
        sqrtQuery = math.sqrt(sqrtQuery)

        sim = numerator / (sqrtDoc * sqrtQuery)
        return sim

    def calculate_rank(docs_tfidf, query_w):
        rank = []
        for tfidf in docs_tfidf:
            rank.append(sim(tfidf, query_w))
        rank.sort()
        return rank


