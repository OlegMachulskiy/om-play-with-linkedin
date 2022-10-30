import argparse
import json
import logging
from nltk.corpus import stopwords

import nltk
from nltk import word_tokenize, Text

from DbStructure import DbStructure


class JobsCategorizer:
    def __init__(self):
        self.db = DbStructure()
        with open("init.json", "r") as init_file:
            self.config = json.load(init_file)


    def run(self):
        stop_words = [",", "?"]
        stop_words.extend(stopwords.words('english'))
        stop_words.extend(stopwords.words('german'))

        fetchall = self.db.connect.execute("SELECT job_id, full_text, job_title, location FROM JOB_RAW_DATA").fetchall()

        for row in fetchall:
            job_id = row[0]
            raw_text = row[1].lower()
            tokens = word_tokenize(raw_text)
            text = Text(tokens)
            fd = nltk.FreqDist(text)

            technically_relevant = sum([fd[k] for k in self.config["technically_relevant"]]) / len(text)
            position_relevant = sum([fd[k] for k in self.config["position_relevant"]]) / len(text)
            area_relevant = sum([fd[k] for k in self.config["area_relevant"]]) / len(text)
            relocation_relevant = sum([fd[k] for k in self.config["relocation_relevant"]]) / len(text)


            fd_bigrams = nltk.FreqDist([b for b in nltk.bigrams(text) if b[0] not in stop_words and b[1] not in stop_words])

            collocations = fd_bigrams.most_common(10)

            logging.info("%s\t%s\t%s\t%s", )
            self.db.connect.execute("""delete from JOB_ANALYSIS where job_id=?""", [job_id])
            self.db.connect.execute(
                """insert into JOB_ANALYSIS (job_id, technically_relevant, position_relevant, area_relevant, relocation_relevant, collocations ) values (?,?,?,?,?,?)""",
                [job_id, technically_relevant, position_relevant, area_relevant, relocation_relevant,
                 str(collocations)])
            self.db.connect.commit()


if __name__ == '__main__':
    logging.basicConfig(filename='categorize-jobs.py.log', level=logging.DEBUG, filemode="w", encoding="UTF-8")
    argparser = argparse.ArgumentParser(prog='scrap-profiles',
                                        description='omachulski scripts to count update jobs statistics',
                                        epilog='src: https://github.com/OlegMachulskiy/om-play-with-linkedin')
    args = argparser.parse_args()

    c = JobsCategorizer()
    c.run()
