from webdriver_manager import driver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from root.repositories.WebdriverDbAccessor import WebdriverDbAccessor
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

from root.modules.webdriver.helpers.webdrivers.AtcoderWebdriver import AtcoderWebdriver
from root.modules.webdriver.helpers.webdrivers.CodeforcesWebdriver import CodeforcesWebdriver
from root.modules.webdriver.helpers.webdrivers.GymWebdriver import GymWebdriver
from root.modules.webdriver.helpers.webdrivers.TLXWebdriver import TLXWebdriver
from root.modules.webdriver.helpers.webdrivers.OjUzWebdriver import OjUzWebdriver

import os


class WebdriverService:
    def __init__(self, *args, **kwargs):
        # self.init_driver()
        self.db_accessor = WebdriverDbAccessor()
        self.webdriver = {
            'Atcoder': AtcoderWebdriver(),
            'Codeforces': CodeforcesWebdriver(),
            'TLX': TLXWebdriver(),
            'Gym': GymWebdriver(),
            'OjUz': OjUzWebdriver()
        }

    def init_driver(self):
        self.opt = Options()
        if os.environ.get('ENV') == 'production':
            self.opt.add_argument('--headless')
            self.opt.add_argument('--disable-dev-shm-usage')
            self.opt.add_argument('--disable-gpu')
            self.opt.add_argument('--no-sandbox')
            self.opt.add_argument('--remote-debugging-port=9222')

        # self.opt.add_argument('--headless')
        self.driver = webdriver.Chrome(
            ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install(), chrome_options=self.opt)

        if os.environ.get('ENV') == 'production':
            self.driver.set_window_size(950, 800)

    def submit_solution(self, oj_name, oj_problem_code, source_code, user_id, problemset=None):
        result = None
        self.init_driver()
        webdriver = self.webdriver.get(oj_name)
        result = webdriver.submit_solution(
            oj_name, oj_problem_code, source_code, user_id, self.driver, problemset)
        return result

    def get_crawl_request_by_id(self, crawl_request_id):
        return self.db_accessor.get_crawl_request_by_id(crawl_request_id)
