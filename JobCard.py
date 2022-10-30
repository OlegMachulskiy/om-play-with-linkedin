import logging
import re
from time import sleep

from bs4 import BeautifulSoup

# JobCard - parse LinkedIn job page with already opened job description
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class JobDetailsItem:
    def __init__(self, element):
        self.insight_text = BeautifulSoup(element.get_attribute("innerHTML"), features="html.parser").get_text()
        self.insight_href = ""

        links = element.find_elements(By.XPATH, """./a """)
        if (len(links) > 0):
            self.insight_href = links[0].get_attribute("href")
            self.insight_text = links[0].text


class JobCard:
    def __init__(self, webdriver, job_link):
        self.webdriver = webdriver

        self.job_title = job_link.text
        self.job_href = job_link.get_attribute("href")
        self.jobId = re.search("/jobs/view/([0-9]+)/.+", self.job_href).group(1)
        logging.debug("Parsed id=%s from href: %s", self.jobId, self.job_href)
        # <a data-control-id="WoDK4MCAZ65F0+KHlkLT+Q==" tabindex="0" href="/jobs/view/2904894086/?eBP=JOB_SEARCH_ORGANIC&amp;refId=PeqWckmTbHQBk6CWHCra%2BQ%3D%3D&amp;trackingId=WoDK4MCAZ65F0%2BKHlkLT%2BQ%3D%3D&amp;trk=flagship3_search_srp_jobs" id="ember621" class="disabled ember-view job-card-container__link job-card-list__title">
        self.job_body_element = self.webdriver.find_element(By.XPATH,
                                                            """// div[@class="job-view-layout jobs-details"]""")
        self.full_html = self.job_body_element.get_attribute('innerHTML')
        self.full_text = BeautifulSoup(self.full_html, features="html.parser").get_text()

        location_element = self.job_body_element.find_element(By.XPATH, """ // div[@class="jobs-unified-top-card__primary-description"] // span[@class="jobs-unified-top-card__bullet"]""")
        self.location = BeautifulSoup(location_element.get_attribute('innerHTML'), features="html.parser").get_text()


    def parseAttributes(self):
        job_card = self.webdriver.find_element(By.XPATH,
                                               """// div[@class = "jobs-unified-top-card__content--two-pane"]""")
        company_link_as = job_card.find_elements(By.XPATH,
                                                 """//span[@class = "jobs-unified-top-card__company-name"] / a """)

        if len(company_link_as) > 0:
            self.company_name = company_link_as[0].text
            self.company_href = company_link_as[0].get_attribute("href")
        else:
            company_link_span = job_card.find_elements(By.XPATH,
                                                       """//span[@class = "jobs-unified-top-card__company-name"]  """)
            if len(company_link_span) > 0:
                self.company_name = self.full_text = BeautifulSoup(
                    company_link_span[0].get_attribute('innerHTML')).get_text()
                self.company_href = company_link_span[0].get_attribute('innerHTML')
            else:
                self.company_name = "cannot parse"
                self.company_href = "cannot parse"


        job_insights = job_card.find_elements(By.XPATH, """.//li[@class="jobs-unified-top-card__job-insight"]/span""")
        self.job_details_items = [JobDetailsItem(elem) for elem in job_insights]

        pass

    @staticmethod
    def parseJobId(job_link):
        job_href = job_link.get_attribute("href")
        jobId = re.search("/jobs/view/([0-9]+)/.+", job_href).group(1)
        return jobId

    @staticmethod
    def checkExistsInDB(connect, job_id):
        dataFromSql = connect.execute("SELECT job_id FROM JOB_RAW_DATA WHERE job_id=?", [job_id])
        fetchall = dataFromSql.fetchall()
        if len(fetchall) > 0:
            return True
        else:
            return False

    def save_to_db(self, connect):
        if self.checkExistsInDB(connect, self.jobId):
            return

        sql = """INSERT INTO JOB_RAW_DATA (job_id, job_href, full_html, job_title, 
        company_href, company_name, full_text, location)
         values (?, ?, ?, ?, ?, ?, ?, ?)"""
        connect.execute(sql, [self.jobId, self.job_href, self.full_html, self.job_title, self.company_href,
                              self.company_name, self.full_text, self.location])

        connect.execute("""delete from JOB_DETAILS where job_id=?""", [self.jobId])

        for detail in self.job_details_items:
            connect.execute("""insert into JOB_DETAILS (job_id, insight_text, insight_href) values (?, ?, ?)""",
                            [self.jobId, detail.insight_text, detail.insight_href])

        connect.commit()


if __name__ == '__main__':
    href = "/jobs/view/2904894086/?eBP=JOB_SEARCH_ORGANIC&amp;refId=PeqWckmTbHQBk6CWHCra%2BQ%3D%3D&amp;trackingId=WoDK4MCAZ65F0%2BKHlkLT%2BQ%3D%3D&amp;trk=flagship3_search_srp_jobs"
    m = re.search("/jobs/view/([0-9]+)/.+", href)
    print(m.group(1))
