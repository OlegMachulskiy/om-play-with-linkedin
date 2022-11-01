import argparse
import json
import logging
import traceback
from time import sleep
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from persistence.DbStructure import DbStructure
from scrapper.JobCard import JobCard, parseJobId


def get_filter_variations(scrapper_config):
    result = set()
    for url in scrapper_config["filter"]:
        result.add(url)

        for keyword in scrapper_config["filter-keywords"]:
            url_parts = list(urlparse(url))
            query = dict(parse_qsl(url_parts[4]))
            query['keywords'] = keyword

            for sortBy in scrapper_config["filter-sortBy"]:
                query['sortBy'] = sortBy
                url_parts[4] = urlencode(query)
                result.add(urlunparse(url_parts))

    return result


class ProfilesScrapper:
    def __init__(self, chromedriver_path):
        self.chromedriver_path = chromedriver_path
        self.db = DbStructure()
        self.db.info()
        with open("secret.json", "r") as secret_file:
            self.secret = json.load(secret_file)

    def prepareChromeOptions(self):
        options = webdriver.ChromeOptions()
        # https://www.software-testing-tutorials-automation.com/2016/05/selenium-loading-google-chrome-driver.html
        # FoxyProxy path: C:/Users/omachulski/AppData/Local/Google/Chrome/User Data/Default/Extensions/gcknhkkoolaabfmlnjonogaaifnjlfnp/3.0.7.1_0

        # options.add_extension("C:/Users/omachulski/AppData/Local/Google/Chrome/User Data/Default/Extensions/gcknhkkoolaabfmlnjonogaaifnjlfnp/3.0.7.1_0.crx")
        # options.add_argument("load-extension=C:/Users/omachulski/AppData/Local/Google/Chrome/User Data/Default/Extensions/gcknhkkoolaabfmlnjonogaaifnjlfnp/3.0.7.1_0/")

        # options.add_argument("start-maximized")
        # options.add_argument("user-data-dir=C:/Users/omachulski/AppData/Local/Google/Chrome/User Data/Default")

        # options.add_argument("enable-default-apps")

        if ("proxy-host" in self.secret.keys()) and ("proxy-port" in self.secret.keys()):
            host = self.secret["proxy-host"]
            port = self.secret["proxy-port"]
            options.add_argument("--proxy-server=socks5://{}:{}".format(host, port))

        # connect to existing chrome browser window. Please see  https://abodeqa.com/how-to-connect-selenium-to-existing-chrome-browser/
        options.add_experimental_option("debuggerAddress", "localhost:9222")

        return options

    def run(self):
        webService = Service(self.chromedriver_path)
        web_driver = webdriver.Chrome(service=webService, options=self.prepareChromeOptions())

        # buttons = web_driver.find_elements(By.TAG_NAME, "button")
        with open("init.json", "r") as init_file:
            scrapper_config = json.load(init_file)
            filters_to_start_with = get_filter_variations(scrapper_config)

            for filter in filters_to_start_with:
                logging.debug("loading linkedin filter page: %s", filter)
                web_driver.get(filter)
                logging.debug("loading linkedin filter page DONE: %s", filter)

                xpath_jobs = """// ul[@class = "scaffold-layout__list-container"] / li // a[@class="disabled ember-view job-card-container__link job-card-list__title"]"""

                already_clicked = set()
                job_links = web_driver.find_elements(By.XPATH, xpath_jobs)
                number_of_iterations = 25
                while (True):
                    if len(job_links) >= 25 or number_of_iterations < 0:
                        break
                    number_of_iterations -= 1

                    for job_link in job_links:
                        if job_link not in already_clicked and not JobCard.checkExistsInDB(self.db.connect,
                                                                                           parseJobId(job_link)):
                            try:
                                job_link.click()
                                sleep(1)

                                el = WebDriverWait(web_driver, timeout=5). \
                                    until(lambda d: d.find_element(By.XPATH,
                                                                   """//div[@class="jobs-unified-top-card__content--two-pane"] // li[@class="jobs-unified-top-card__job-insight"] """))

                                job_card = JobCard(job_link=job_link, webdriver=web_driver)
                                job_card.parseAttributes()
                                job_card.save_to_db(connect=self.db.connect)
                                already_clicked.add(job_link)

                                scroll_origin = ScrollOrigin.from_element(job_links[len(job_links) - 1])
                                ActionChains(web_driver) \
                                    .scroll_from_origin(scroll_origin, 0, 300) \
                                    .scroll_from_origin(scroll_origin, 0, 300) \
                                    .scroll_from_origin(scroll_origin, 0, 300) \
                                    .perform()

                            except Exception as ex:
                                print(traceback.format_exception(ex))
                                logging.error("Something happened {}, skipping this job: {}".format(ex, job_link.text))
                                continue

                        job_links = web_driver.find_elements(By.XPATH, xpath_jobs)


if __name__ == '__main__':
    logging.basicConfig(filename='scrap_profiles.py.log', level=logging.DEBUG, filemode="w", encoding="UTF-8")
    argparser = argparse.ArgumentParser(prog='scrap-profiles',
                                        description='omachulski scripts to parse something from linkedin',
                                        epilog='src: https://github.com/OlegMachulskiy/om-play-with-linkedin')

    argparser.add_argument("-d", "--webdriver", default="e:/usr/webdriver/chromedriver")
    args = argparser.parse_args()

    i = ProfilesScrapper(chromedriver_path=args.webdriver)
    i.run()
