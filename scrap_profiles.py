import logging

from selenium import webdriver
import json

from selenium.webdriver.common.by import By

from DbStructure import DbStructure


class ProfilesScrapper:
    def __init__(self):
        dbs = DbStructure()
        dbs.info()
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

        host = self.secret["proxy-host"]
        port = self.secret["proxy-port"]
        options.add_argument("--proxy-server=socks5://{}:{}".format(host, port))

        options.add_experimental_option("debuggerAddress", "localhost:9222")
        return options

    def run(self):
        driver = webdriver.Chrome('d:/usr/chromedriver/chromedriver', options=self.prepareChromeOptions())
        login_page = driver.get('https://www.linkedin.com/jobs/')
        # driver.find_element(By.ID, "session_key").send_keys(self.secret["user"])
        # driver.find_element(By.ID, "session_password").send_keys(self.secret["password"])

        buttons = driver.find_elements(By.TAG_NAME, "button")
        pass


if __name__ == '__main__':
    logging.basicConfig(filename='scrap_profiles.py.log', level=logging.DEBUG, filemode="w", encoding="UTF-8")
    i = ProfilesScrapper()
    i.run()
