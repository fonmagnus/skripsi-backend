from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from webdriver_manager.chrome import ChromeDriverManager
import time
from root.modules.webdriver.models import OJLoginAccountInfo, CrawlRequest
from .BaseWebdriver import BaseWebdriver
from root.modules.problems.models import OJSubmission
import threading
from datetime import datetime
import os


class AtcoderWebdriver(BaseWebdriver):
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://atcoder.jp/contests/'
        BaseWebdriver.__init__(self, *args, **kwargs)

    def submit_solution(self, params={}):
        self.pre_submit_solution(params)
        contest_id, problem_no = map(str, self.oj_problem_code.split('_'))
        self.url = self.base_url + \
            str(contest_id) + '/tasks/' + self.oj_problem_code
        self.lang = "C++ (GCC 9.2.1)"

        thread = threading.Thread(
            target=self.do_crawl,
            args=[self.oj_submission]
        )
        thread.setDaemon(True)
        thread.start()
        return self.crawl_request

    def do_crawl(self, oj_submission):
        try:
            self.driver.get(self.url)
            self.do_login()
            if not self.check_login_successful():
                self.do_login(reattempt=True)
            self.post_successful_login()
            self.do_submit()
            submission_id = self.fetch_submission_id()
            self.crawl_request.submission_id = submission_id
            self.crawl_request.status = 'Completed'
            self.crawl_request.save()
            self.oj_submission.submission_id = submission_id
            self.oj_submission.save()
            thread = threading.Thread(
                target=self.keep_fetching_verdict, args=[oj_submission])
            thread.setDaemon(True)
            thread.start()
        except:
            self.mark_submission_error(oj_submission)

    def keep_fetching_verdict(self, oj_submission):
        try:
            while True:
                time.sleep(2)
                self.driver.refresh()
                verdict = self.get_submission_verdict(
                    oj_submission.submission_id, oj_submission.oj_problem_code)

                oj_submission.verdict = verdict.get('verdict')
                oj_submission.status = verdict.get('status')
                oj_submission.score = verdict.get('score', 0)
                oj_submission.save()

                if verdict.get('status') != 'Pending':
                    break
        except Exception as e:
            self.mark_submission_error(oj_submission)

    def do_login(self, reattempt=False):
        if reattempt:
            self.login_account = self.get_random_oj_account(self.oj_name)
        login_link = self.driver.find_element_by_link_text(
            'Sign In').click()
        self.driver.find_element_by_id(
            'username').send_keys(self.login_account.email_or_username)
        self.driver.find_element_by_id(
            'password').send_keys(self.login_account.password)
        self.driver.find_element_by_id(
            'submit').click()

    def check_login_successful(self):
        try:
            time.sleep(3)
            ddelement = Select(
                self.driver.find_element_by_name('data.LanguageId'))
            ddelement.select_by_visible_text(self.lang)
        except:
            return False
        return True

    def do_submit(self):
        time.sleep(4)

        ddelement = Select(
            self.driver.find_element_by_name('data.LanguageId'))
        ddelement.select_by_visible_text(self.lang)

        button = self.driver.find_element_by_xpath(
            '//button[normalize-space()="Toggle Editor"]')
        self.driver.execute_script('arguments[0].click()', button)

        code_editor = self.driver.find_element_by_name(
            'sourceCode').send_keys(self.source_code)

        self.driver.execute_script('arguments[0].click()', button)
        self.driver.find_element_by_id(
            'submit').click()

    def fetch_submission_id(self):
        submit_link = self.driver.find_elements_by_xpath(
            '//a[text()="Detail"]')[0]
        return submit_link.get_attribute('href').split('/')[-1]

    def get_submission_verdict(self, submission_id, oj_problem_code):
        try:
            contest_id = oj_problem_code.split('_')[0]
            submission_url = self.base_url + contest_id + '/submissions/' + submission_id
            self.driver.get(submission_url)

            status_td = self.driver.find_element_by_id('judge-status')
            status = status_td.find_element_by_tag_name(
                'span').get_attribute('data-original-title')

            if status == 'Accepted':
                return {
                    'verdict': status,
                    'status': status,
                    'score': 100
                }
            elif status == 'Waiting for Judging' or status == 'Judging':
                return {
                    'verdict': status,
                    'status': 'Pending'
                }
            else:
                return {
                    'verdict': status,
                    'status': 'Rejected'
                }

        except:
            pass
