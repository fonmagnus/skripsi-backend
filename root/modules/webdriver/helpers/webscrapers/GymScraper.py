import requests
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium import webdriver

import os


class GymScraper:
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://codeforces.com/gym/'

    def scrap(self, oj_problem_code):
        self.opt = Options()
        if os.environ.get('ENV') == 'production':
            self.opt.add_argument('--headless')
        # self.opt.add_argument('--headless')
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=self.opt)
        contest_id, problem_no = oj_problem_code[:-1], oj_problem_code[-1:]
        self.url = self.base_url + str(contest_id) + '/problem/' + problem_no
        self.oj_problem_code = oj_problem_code

        # page = requests.get(self.url)
        # soup = BeautifulSoup(page.content, "html.parser")
        self.driver.get(self.url)
        try:
            return self.get_dict()
        except Exception as e:
            self.driver.quit()
            raise e

    def get_dict(self):
        problemset_title = self.driver.find_element_by_class_name(
            'title').get_attribute('innerText').split('. ')[1]

        time_limit = self.driver.find_element_by_class_name(
            'time-limit').get_attribute('innerText').lstrip('time limit per test')

        memory_limit = self.driver.find_element_by_class_name(
            'memory-limit').get_attribute('innerText').lstrip('memory limit per test')

        js_string = 'var elements = document.getElementsByClassName(\"header\"); while(elements.length > 0) elements[0].parentNode.removeChild(elements[0]);'
        self.driver.execute_script(js_string)
        js_string = 'var elements = document.getElementsByClassName(\"MathJax_Preview\"); while(elements.length > 0) elements[0].parentNode.removeChild(elements[0]);'
        self.driver.execute_script(js_string)
        js_string = 'var elements = document.getElementsByClassName(\"MathJax\"); while(elements.length > 0) elements[0].parentNode.removeChild(elements[0]);'
        self.driver.execute_script(js_string)
        js_string = 'var elements = document.getElementsByClassName(\"input-output-copier\"); while(elements.length > 0) elements[0].parentNode.removeChild(elements[0]);'
        self.driver.execute_script(js_string)
        body = self.driver.find_element_by_class_name(
            'problem-statement').get_attribute('innerHTML')

        try:
            input_format = self.driver.find_element_by_class_name(
                'input-specification').get_attribute('innerText').lstrip('Input')
        except:
            input_format = ''

        try:
            output_format = self.driver.find_element_by_class_name(
                'output-specification').get_attribute('innerText').lstrip('Output')
        except:
            output_format = ''

        example = str(self.driver.find_element_by_class_name('sample-test'))

        try:
            notes = self.driver.find_element_by_class_name('note')
            if notes is not None:
                notes = notes.get_attribute('innerText')
        except:
            notes = ''

        # for div in body.find_all("div", {'class': 'header'}):
        #     div.decompose()
        # body = str(body)
        self.driver.quit()

        return {
            'oj_name': 'Gym',
            'oj_problem_code': self.oj_problem_code,
            'url': self.url,
            'title': problemset_title,
            'body': body,
            'time_limit': time_limit,
            'memory_limit': memory_limit,
            'input_format': input_format,
            'output_format': output_format,
            'example': example,
            'notes': notes,
        }
