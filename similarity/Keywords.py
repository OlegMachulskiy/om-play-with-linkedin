import hashlib
import json

import nltk
from nltk import word_tokenize

from similarity import AbstractCalculator


class KeywordsCalculator(AbstractCalculator):
    def __init__(self, technically_relevant, position_relevant, area_relevant, relocation_relevant, irrelevant_relevant):
        self.technically_relevant = technically_relevant
        self.position_relevant = position_relevant
        self.area_relevant = area_relevant
        self.relocation_relevant = relocation_relevant
        self.irrelevant_relevant = irrelevant_relevant

    def get_hash(self):
        m = hashlib.sha256()
        m.update(str(self.technically_relevant).encode("utf-8"))
        m.update(str(self.position_relevant).encode("utf-8"))
        m.update(str(self.area_relevant).encode("utf-8"))
        m.update(str(self.relocation_relevant).encode("utf-8"))
        m.update(str(self.irrelevant_relevant).encode("utf-8"))
        return m.hexdigest()

    def calc_similarity(self, job_desc):
        tokens = word_tokenize(job_desc.lower())
        text = nltk.Text(tokens)
        fd = nltk.FreqDist(text)
        textLen = len(text) if len(text) > 0 else 1

        result = {}
        result["technically_relevant"] = sum([fd[k] for k in self.technically_relevant]) / textLen
        result["position_relevant"] = sum([fd[k] for k in self.position_relevant]) / textLen
        result["area_relevant"] = sum([fd[k] for k in self.area_relevant]) / textLen
        result["relocation_relevant"] = sum([fd[k] for k in self.relocation_relevant]) / textLen
        result["irrelevant_relevant"] = sum([fd[k] for k in self.irrelevant_relevant]) / textLen

        return result


if __name__ == '__main__':
    config = json.load(open("../init.json", "r"))
    kc = KeywordsCalculator(config["technically_relevant"],
                            config["position_relevant"],
                            config["area_relevant"],
                            config["relocation_relevant"],
                            config["irrelevant_relevant"])
    res = kc.calc_similarity(
        """ 
        We are specialist in Web/Mobile Application Development,E-Commerce solutions, iPhone, 
        iPad and Android Apps development Services,SEO Services and Content Writing. IF you interest I would love 
        to share more detail about our company with our work portfolio. 
        java xml json python
        """)
    print(res)
