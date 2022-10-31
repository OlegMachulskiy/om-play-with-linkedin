import hashlib


class AbstractCalculator:
    def calc_similarity(self, job_desc):
        return {}

    def get_hash(self):
        m = hashlib.sha256()
        m.update("nothing")
        return m.hexdigest()

