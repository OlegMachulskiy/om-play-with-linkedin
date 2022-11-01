import hashlib
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


class TextSimilarityCalculator(AbstractCalculator):

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

        nltk_cosine_result = {}

        for f in self.files:
            low_text = open(self.corpus_dir + "/" + f, "r", encoding="utf-8").read().lower()

            ##### nltk:
            sim_nltk = cosine_sim(job_desc, low_text)
            nltk_cosine_result[f] = sim_nltk

        return nltk_cosine_result


if __name__ == '__main__':
    calc = TextSimilarityCalculator("../corpus/multi-axis")

    res = calc.calc_similarity(
        """ 
        IT Project Manager duties and responsibilities
IT Project Managers are responsible for overseeing all aspects of any project in a company’s IT department, which includes managing a team of employees to ensure projects are completed on time and within their specified budgets. Some of an IT Project Manager’s day-to-day duties include:

Setting project goals and coming up with plans to meet those goals
Maintaining project timeframes, budgeting estimates and status reports
Managing resources for projects, such as computer equipment and employees
Coordinating project team members and developing schedules and individual responsibilities
Implementing IT strategies that deliver projects on schedule and within budget
Using project management tools to track project performance and schedule adherence
Conducting risk assessments for projects
Organizing meetings to discuss project goals and progress

        """)
    print(res, calc.get_hash())

    res = calc.calc_similarity(
        """ 
       We are seeking a hard-working and reliable construction worker to join our team. You will participate in a variety of construction projects and follow construction plans and instructions from the site supervisor. Although experience isn't essential, you will have to be physically fit and a fast learner.

To be successful in this position, you will work well as part of a team, enjoy working outdoors, and be able to perform strenuous physical tasks.

Construction Worker Responsibilities:
Preparing construction sites, materials, and tools.
Loading and unloading of materials, tools, and equipment.
Removing debris, garbage, and dangerous materials from sites.
Assembling and breaking down barricades, temporary structures, and scaffolding.
Assisting contractors, e.g. electricians and painters, as required.
Assisting with transport and operation of heavy machinery and equipment.
Regulating traffic and erecting traffic signs.
Following all health and safety regulations.
Digging holes, tunnels, and shafts.
Mixing, pouring, and leveling concrete.
Construction Worker Job Requirements:
No formal qualification is required, although a high school diploma may be preferred.
Similar work experience may be beneficial.
Licensure to work with hazardous materials may be required.
Willingness to undertake training if necessary.
Be mild-tempered and a team player.
Be healthy, strong, and fit.
        """)
    print(res, calc.get_hash())
