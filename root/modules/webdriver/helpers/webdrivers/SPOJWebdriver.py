from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

import time
from root.modules.webdriver.models import OJLoginAccountInfo, CrawlRequest
from root.modules.problems.models import OJSubmission
from .BaseWebdriver import BaseWebdriver
import threading
from datetime import datetime
import os


class SPOJWebdriver(BaseWebdriver):
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://www.spoj.com/'
        BaseWebdriver.__init__(self, *args, **kwargs)

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass

    def submit_solution(self, params={}):
        self.pre_submit_solution(params)
        self.url = self.base_url + 'problems/' + self.oj_problem_code
        self.lang = "C++14 (gcc 8.3)"

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
            self.driver.get(self.url)
            self.do_submit()
            submission_id = self.fetch_submission_id()
            self.crawl_request.submission_id = submission_id
            self.crawl_request.status = 'Completed'
            self.crawl_request.save()
            oj_submission.submission_id = submission_id
            oj_submission.save()
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
        except:
            self.mark_submission_error(oj_submission)

        self.driver.quit()

    def do_login(self):
        login_link = self.driver.find_element_by_link_text('sign in')
        login_link.click()
        self.driver.find_element_by_name(
            'login_user').send_keys(self.login_account.email_or_username)
        self.driver.find_element_by_name(
            'password').send_keys(self.login_account.password)
        self.driver.find_element_by_xpath(
            '//button[normalize-space()="sign in"]').click()
        print('Login at :', datetime.now())
        self.login_account.last_login = datetime.now()
        self.login_account.save()

    def do_submit(self):
        time.sleep(4)
        print('Submitting solution . . .')
        submit_link = self.driver.find_element_by_id('problem-btn-submit')
        self.driver.execute_script('arguments[0].click()', submit_link)

        ddelement = Select(
            self.driver.find_element_by_id('lang'))
        ddelement.select_by_visible_text(self.lang)

        filename = "SPOJ-" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".cpp"
        print(filename)
        f = open(filename, "w")
        f.write(self.source_code)
        print('File:', f)
        f.close()

        uploader = self.driver.find_element_by_id('subm_file')
        uploader.send_keys(os.getcwd() + "/" + filename)
        btn = self.driver.find_element_by_id(
            'submit')
        self.driver.execute_script('arguments[0].click()', btn)
        print('Uploading . . .')
        os.remove(filename)
        print('Done upload!')

    def fetch_submission_id(self):
        url = self.base_url + 'status/' + self.login_account.email_or_username
        self.driver.get(url)
        td = self.driver.find_element_by_class_name(
            'sourcelink').get_attribute('innerText')
        return td

    def get_submission_verdict(self, submission_id, oj_problem_code):
        try:
            crawl_request = CrawlRequest.objects.get(
                oj_name='SPOJ', submission_id=submission_id)
            crawler_account = crawl_request.oj_login_account_info
            url = self.base_url + 'status/' + crawler_account.email_or_username
            self.driver.get(url)
            status_text = self.driver.find_element_by_id(
                'statusres_' + submission_id).get_attribute('innerText')
            status_text = status_text.replace('edit', '')
            status_text = status_text.replace('ideone it', '')
            status_text = status_text.strip()

            if status_text == 'accepted':
                return {
                    'verdict': 'Accepted',
                    'status': 'Accepted',
                    'score': 100
                }
            elif 'running' in status_text or 'compiling' in status_text or 'waiting' in status_text:
                return {
                    'verdict': status_text,
                    'status': 'Pending'
                }
            else:
                return {
                    'verdict': status_text,
                    'status': 'Rejected'
                }
        except:
            return {
                'verdict': 'Error',
                'status': 'Error'
            }
