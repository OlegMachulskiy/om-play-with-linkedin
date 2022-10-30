import logging
import re

# JobCard - parse LinkedIn job page with already opened job description
from selenium.webdriver.common.by import By


class JobCard:
    def __init__(self, webdriver, job_href):
        self.webdriver = webdriver
        self.job_href = job_href
        self.jobId = re.search("/jobs/view/([0-9]+)/.+",  job_href).group(1)
        logging.debug("Parsed id=%s from href: %s", self.jobId, self.job_href)
        # <a data-control-id="WoDK4MCAZ65F0+KHlkLT+Q==" tabindex="0" href="/jobs/view/2904894086/?eBP=JOB_SEARCH_ORGANIC&amp;refId=PeqWckmTbHQBk6CWHCra%2BQ%3D%3D&amp;trackingId=WoDK4MCAZ65F0%2BKHlkLT%2BQ%3D%3D&amp;trk=flagship3_search_srp_jobs" id="ember621" class="disabled ember-view job-card-container__link job-card-list__title">
        self.job_body_element = self.webdriver.find_element(By.XPATH, """// div[@class="job-view-layout jobs-details"]""")
        self.full_html = self.job_body_element.get_attribute('innerHTML')

    def parseAttributes(self):
        pass


    def save_to_db(self, connect):
        # dataFromSql = self.connect.execute("SELECT JobId FROM JOB_RAW_DATA WHERE JobId=?", [self.jobId] )
        # fetchall = dataFromSql.fetchall()
        # if len(fetchall) > 0:
        #     logging.debug("record already exists: %s")
        # self.connect.
        sql = """INSERT INTO JOB_RAW_DATA (job_id, job_href, full_html) values (?, ?, ?)"""
        connect.execute(sql, [self.jobId, self.job_href, self.full_html])
        connect.commit()



if __name__ == '__main__':
    href = "/jobs/view/2904894086/?eBP=JOB_SEARCH_ORGANIC&amp;refId=PeqWckmTbHQBk6CWHCra%2BQ%3D%3D&amp;trackingId=WoDK4MCAZ65F0%2BKHlkLT%2BQ%3D%3D&amp;trk=flagship3_search_srp_jobs"
    m = re.search("/jobs/view/([0-9]+)/.+", href)
    print( m.group(1) )
