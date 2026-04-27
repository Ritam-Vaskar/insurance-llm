import math
from collections import Counter
import re

def tokenize(text):
    text = text.lower()
    return re.findall(r'\w+', text)

class BM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.doc_lengths = [len(doc) for doc in corpus]
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_count = len(corpus)
        
        df = Counter()
        for doc in corpus:
            self.doc_freqs.append(Counter(doc))
            for word in set(doc):
                df[word] += 1
                
        for word, count in df.items():
            self.idf[word] = math.log(1 + (self.doc_count - count + 0.5) / (count + 0.5))

    def get_scores(self, query):
        scores = [0] * self.doc_count
        for word in query:
            if word not in self.idf:
                continue
            for i, doc in enumerate(self.corpus):
                freq = self.doc_freqs[i][word]
                if freq == 0:
                    continue
                score = self.idf[word] * (freq * (self.k1 + 1)) / (
                    freq + self.k1 * (1 - self.b + self.b * self.doc_lengths[i] / self.avg_doc_length)
                )
                scores[i] += score
        return scores
