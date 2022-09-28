from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from webdriver_manager.chrome import ChromeDriverManager
import time
from root.modules.webdriver.models import OJLoginAccountInfo, CrawlRequest
from root.modules.problems.models import OJSubmission
import threading
from datetime import datetime
import os


class AtcoderWebdriver:
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://atcoder.jp/contests/'
        self.driver = kwargs.get('driver')

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass

    def submit_solution(self, oj_name, oj_problem_code, source_code, user_id, driver, problemset=None):
        self.driver = driver
        contest_id, problem_no = map(str, oj_problem_code.split('_'))
        self.url = self.base_url + \
            str(contest_id) + '/tasks/' + oj_problem_code
        self.lang = "C++ (GCC 9.2.1)"
        self.source_code = source_code

        login_account = OJLoginAccountInfo.objects.filter(
            oj_name='Atcoder').order_by('?').first()

        crawl_request = CrawlRequest.objects.create(
            oj_name=oj_name, oj_login_account_info=login_account)

        oj_submission = OJSubmission.objects.create(
            oj_name=oj_name,
            source_code=source_code,
            user_id=user_id,
            submission_id=None,
            verdict='Pending',
            oj_login_account_info=login_account,
            oj_problem_code=oj_problem_code,
            problemset=problemset
        )

        thread = threading.Thread(target=self.do_crawl, args=[
                                  self.url, crawl_request, oj_name, source_code, user_id, oj_problem_code, login_account, oj_submission])
        thread.setDaemon(True)
        thread.start()
        return crawl_request

    def do_crawl(self, url, crawl_request, oj_name, source_code, user_id, oj_problem_code, login_account, oj_submission):
        try:
            self.driver.get(url)
            self.do_login(login_account)
            self.do_submit()
            submission_id = self.fetch_submission_id()
            crawl_request.submission_id = submission_id
            crawl_request.status = 'Completed'
            crawl_request.save()
            oj_submission.submission_id = submission_id
            oj_submission.save()
            thread = threading.Thread(
                target=self.keep_fetching_verdict, args=[oj_submission])
            thread.setDaemon(True)
            thread.start()
        except:
            self.driver.quit()

    def keep_fetching_verdict(self, oj_submission):
        while True:
            time.sleep(2)
            self.driver.refresh()
            verdict = self.get_submission_verdict(
                oj_submission.submission_id, oj_submission.oj_problem_code, self.driver)

            oj_submission.verdict = verdict.get('verdict')
            oj_submission.status = verdict.get('status')
            oj_submission.score = verdict.get('score', 0)
            oj_submission.save()

            if verdict.get('status') != 'Pending':
                break

        self.driver.quit()

    def do_login(self, login_account):
        try:

            login_link = self.driver.find_element_by_link_text(
                'Sign In').click()
            self.driver.find_element_by_id(
                'username').send_keys(login_account.email_or_username)
            self.driver.find_element_by_id(
                'password').send_keys(login_account.password)
            self.driver.find_element_by_id(
                'submit').click()

            login_account.last_login = datetime.now()
            login_account.save()
        except:
            return

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

    def get_submission_verdict(self, submission_id, oj_problem_code, driver):
        try:
            self.driver = driver
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
