import json
import logging
import argparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from DbStructure import DbStructure
from JobCard import JobCard


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
            for filter in scrapper_config["filter"]:
                logging.debug("loading linkedin filter page: %s", filter)
                web_driver.get(filter)
                logging.debug("loading linkedin filter page DONE: %s", filter)

                joblinks = web_driver.find_elements(By.XPATH,
                                                    """// ul[@class = "scaffold-layout__list-container"] / li // a[@class="disabled ember-view job-card-container__link job-card-list__title"]""")

                for job_link in joblinks:
                    job_href = job_link.get_attribute("href")
                    job_link.click()
                    job_card = JobCard(job_href=job_href, webdriver=web_driver)
                    job_card.parseAttributes()
                    job_card.save_to_db(connect=self.db.connect)


if __name__ == '__main__':
    logging.basicConfig(filename='scrap_profiles.py.log', level=logging.DEBUG, filemode="w", encoding="UTF-8")
    argparser = argparse.ArgumentParser(prog='scrap-profiles',
                                        description='omachulski scripts to parse something from linkedin',
                                        epilog='src: https://github.com/OlegMachulskiy/om-play-with-linkedin')

    argparser.add_argument("-d", "--webdriver", default="e:/usr/webdriver/chromedriver")
    args = argparser.parse_args()

    i = ProfilesScrapper(chromedriver_path=args.webdriver)
    i.run()
