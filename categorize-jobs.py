import argparse
import datetime
import json
import logging
import math
import re

import nltk
from nltk import word_tokenize

from persistence.DbStructure import DbStructure
from similarity.CorpusSimilarity import CorpusSimilarityCalculator
from similarity.Keywords import KeywordsCalculator


class JobsCategorizer:
    def __init__(self):
        self.db = DbStructure()
        self.config = json.load(open("init.json", "r"))

        self.stop_words = [",", "?", "/", ")", "("]
        # self.stop_words.extend(stopwords.words('english'))
        # self.stop_words.extend(stopwords.words('german'))

    def get_text_collocations(self, job_desc):
        text = nltk.Text(word_tokenize(job_desc.lower()))
        fd_bigrams = nltk.FreqDist(
            [b for b in nltk.bigrams(text) if b[0] not in self.stop_words and b[1] not in self.stop_words])

        return fd_bigrams.most_common(10)

    def update_keywords_calculator(self, job_id, full_text):
        hash_keywords = ""
        sql_res = self.db.connect.execute(
            """select job_id,  hash_keywords from JOB_ANL_KW where job_id=?""",
            [job_id]).fetchall()
        if len(sql_res) > 0:
            hash_keywords = sql_res[0][1]
        else:
            self.db.connect.execute(
                """insert into JOB_ANL_KW (job_id, hash_keywords ) values (?,?)""",
                [job_id, ""]
            )

        kc = KeywordsCalculator(self.config["technically_relevant"],
                                self.config["position_relevant"],
                                self.config["area_relevant"],
                                self.config["relocation_relevant"],
                                self.config["irrelevant_relevant"])

        if hash_keywords != kc.get_hash():
            result = kc.calc_similarity(full_text)

            self.db.connect.execute(
                """update JOB_ANL_KW set 
                    technically_relevant=?, 
                    position_relevant=?, 
                    area_relevant=?, 
                    relocation_relevant=?,
                    irrelevant_relevant=?,
                    hash_keywords=?, 
                    updated_at = ? 
                    WHERE job_id=?""",
                [math.log(1 + result['technically_relevant']),
                 math.log(1 + result['position_relevant']),
                 math.log(1 + result['area_relevant']),
                 math.log(1 + result['relocation_relevant']),
                 math.log(1 + result['irrelevant_relevant']),
                 kc.get_hash(),
                 datetime.datetime.now(),
                 job_id])

    def update_similarity_calculator(self, job_id, full_text):
        hash_relevant = ""
        hash_irrelevant = ""
        sql_res = self.db.connect.execute(
            """select job_id, hash_relevant, hash_irrelevant  from JOB_ANL_SIMILARITY where job_id=?""",
            [job_id]).fetchall()
        if len(sql_res) > 0:
            hash_relevant = sql_res[0][1]
            hash_irrelevant = sql_res[0][2]
        else:
            self.db.connect.execute(
                """insert into JOB_ANL_SIMILARITY (job_id,  hash_relevant, hash_irrelevant ) values (?,?,?)""",
                [job_id, "", ""]
            )
            # str(self.get_text_collocations(full_text)),

        corpus_calc = CorpusSimilarityCalculator("./corpus/relevant")
        if hash_relevant != corpus_calc.get_hash():
            result = corpus_calc.calc_similarity(full_text)
            self.db.connect.execute(
                """update JOB_ANL_SIMILARITY set 
                    cosine_relevant=?, 
                    spacy_relevant=?, 
                    hash_relevant=?, 
                    updated_at = ? 
                    WHERE job_id=?""",
                [math.log(1 + result['cosine_similarity']),
                 math.log(1 + result['spacy_similarity']),
                 corpus_calc.get_hash(),
                 datetime.datetime.now(),
                 job_id])

        corpus_irrelevant_calc = CorpusSimilarityCalculator("./corpus/irrelevant")
        if hash_irrelevant != corpus_irrelevant_calc.get_hash():
            result = corpus_irrelevant_calc.calc_similarity(full_text)
            self.db.connect.execute(
                """update JOB_ANL_SIMILARITY set 
                    cosine_irrelevant=?, 
                    spacy_irrelevant=?, 
                    hash_irrelevant=?, 
                    updated_at = ? 
                    WHERE job_id=?""",
                [math.log(1 + result['cosine_similarity']),
                 math.log(1 + result['spacy_similarity']),
                 corpus_irrelevant_calc.get_hash(),
                 datetime.datetime.now(),
                 job_id])

    def run(self):

        fetchall = self.db.connect.execute("SELECT job_id, full_text, job_title, location FROM JOB_RAW_DATA").fetchall()

        counter = len(fetchall)
        for row in fetchall:
            counter -= 1
            if counter % 50 == 0:
                print("Left to process:{}%".format(int(counter * 100 / len(fetchall))))
            logging.info("%s\t%s\t%s", row[0], row[2], re.sub("[^a-zA-Z0-9 ]+", "", row[3]))

            job_id = row[0]
            hash_keywords = ""
            hash_corpus = ""
            hash_corpus_irrelevant = ""

            self.update_keywords_calculator(job_id, row[1])
            self.update_similarity_calculator(job_id, row[1])

            self.db.connect.commit()


if __name__ == '__main__':
    logging.basicConfig(filename='categorize-jobs.py.log', level=logging.DEBUG, filemode="w", encoding="UTF-8")
    argparser = argparse.ArgumentParser(prog='scrap-profiles',
                                        description='omachulski scripts to count update jobs statistics',
                                        epilog='src: https://github.com/OlegMachulskiy/om-play-with-linkedin')
    args = argparser.parse_args()

    c = JobsCategorizer()
    c.run()
