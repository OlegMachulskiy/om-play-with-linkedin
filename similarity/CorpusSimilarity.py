import hashlib
import statistics
import string
from os import listdir
from os.path import isfile, join

import nltk
from nltk import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

from similarity import AbstractCalculator

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)


def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]


"""remove punctuation, lowercase, stem"""


def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))


vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')


def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0, 1]


class CorpusSimilarityCalculator(AbstractCalculator):

    def __init__(self, corpus_dir):
        self.corpus_dir = corpus_dir
        self.files = sorted([f for f in listdir(corpus_dir) if isfile(join(corpus_dir, f))])

    def get_hash(self):
        m = hashlib.sha256()
        for f in self.files:
            text = open(self.corpus_dir + "/" + f, "r", encoding="utf-8").read()
            m.update(text.encode("utf-8"))
        return m.hexdigest()

    def calc_similarity(self, job_desc):
        tokens = word_tokenize(job_desc.lower())
        text = nltk.Text(tokens)
        fd = nltk.FreqDist(text)

        cosine_result = []
        for f in self.files:
            low_text = open(self.corpus_dir + "/" + f, "r", encoding="utf-8").read().lower()
            # corpus_tokens = word_tokenize(low_text)
            # corpus_text = nltk.Text(corpus_tokens)
            cosine_result.append(cosine_sim(job_desc, low_text))

        return {"cosine_similarity": statistics.mean(cosine_result)}


if __name__ == '__main__':
    calc = CorpusSimilarityCalculator("../corpus/relevant")
    res = calc.calc_similarity(
        """ 
        We are specialist in Web/Mobile Application Development,E-Commerce solutions, iPhone, 
        iPad and Android Apps development Services,SEO Services and Content Writing. IF you interest I would love 
        to share more detail about our company with our work portfolio. 
        java xml json python
        """)
    print(calc.get_hash())
    print(res)
