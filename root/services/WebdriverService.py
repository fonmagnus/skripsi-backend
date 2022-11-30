from webdriver_manager import driver
from root.modules.webdriver.helpers.webdrivers.SPOJWebdriver import SPOJWebdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from root.repositories.WebdriverDbAccessor import WebdriverDbAccessor
from webdriver_manager.chrome import ChromeDriverManager

from root.modules.webdriver.helpers.webdrivers.CodeforcesWebdriver import CodeforcesWebdriver
from root.modules.webdriver.helpers.webdrivers.AtcoderWebdriver import AtcoderWebdriver
from root.modules.webdriver.helpers.webdrivers.GymWebdriver import GymWebdriver
from root.modules.webdriver.helpers.webdrivers.SPOJWebdriver import SPOJWebdriver
from root.modules.webdriver.helpers.webdrivers.TLXWebdriver import TLXWebdriver
from root.modules.webdriver.helpers.webdrivers.OjUzWebdriver import OjUzWebdriver

import os


class WebdriverService:
    def __init__(self, *args, **kwargs):
        # self.init_driver()
        self.db_accessor = WebdriverDbAccessor()
        self.webdrivers = {
            'Codeforces': CodeforcesWebdriver,
            'Atcoder': AtcoderWebdriver,
            'Gym': GymWebdriver,
            'SPOJ': SPOJWebdriver,
            'TLX': TLXWebdriver,
            'OjUz': OjUzWebdriver,
        }

    def submit_solution(self, params={}):
        # * create webdriver instance based on OJ name
        WebdriverClass = self.webdrivers.get(params.get('oj_name'))
        if WebdriverClass is None:
            return None

        webdriver_instance = WebdriverClass()
        result = webdriver_instance.submit_solution(params)

        return result

    def get_crawl_request_by_id(self, crawl_request_id):
        return self.db_accessor.get_crawl_request_by_id(crawl_request_id)
