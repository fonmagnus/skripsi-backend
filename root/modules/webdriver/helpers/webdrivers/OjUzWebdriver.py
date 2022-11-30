import json
from re import sub
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import time
from root.modules.webdriver.models import OJLoginAccountInfo, CrawlRequest
from root.modules.problems.models import OJSubmission
from .BaseWebdriver import BaseWebdriver
import threading
from datetime import datetime


class OjUzWebdriver(BaseWebdriver):
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://oj.uz/'
        BaseWebdriver.__init__(self, *args, **kwargs)

    def __del__(self):
        self.driver.quit()

    def submit_solution(self, params={}):
        self.pre_submit_solution(params)
        self.url = self.base_url + 'problem/submit/' + self.oj_problem_code
        self.lang = "C++17 [g++ (Ubuntu 10.2.0-5ubuntu1~20.04) 10.2.0]"

        thread = threading.Thread(
            target=self.do_crawl,
            args=[
                self.url,
                self.oj_problem_code,
                self.oj_submission
            ]
        )
        thread.setDaemon(True)
        thread.start()
        return self.crawl_request

    def do_crawl(self, oj_problem_code, oj_submission):
        try:
            self.driver.get(self.base_url + 'login')
            self.do_login()
            self.driver.get(self.url)
            self.do_submit(oj_problem_code)
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
        except Exception as e:
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
                oj_submission.subtask_results = verdict.get(
                    'subtask_results', "[]")
                oj_submission.save()

                if verdict.get('status') != 'Pending':
                    break
                print(oj_submission.status, oj_submission.verdict)
        except:
            self.mark_submission_error(oj_submission)

        self.driver.quit()

    def do_login(self):
        self.driver.find_element_by_id(
            'email').send_keys(self.login_account.email_or_username)
        self.driver.find_element_by_id(
            'password').send_keys(self.login_account.password)
        login_button = self.driver.find_element_by_xpath(
            '//input[@value="Sign in"]')
        self.driver.execute_script('arguments[0].click()', login_button)
        self.login_account.last_login = datetime.now()
        self.login_account.save()

    def do_submit(self, oj_problem_code):
        ddelement = Select(
            self.driver.find_element_by_id('language'))
        ddelement.select_by_visible_text(self.lang)
        self.source_code = self.source_code.replace("\\n", "\\\\n")

        code_mirror = self.driver.find_element_by_class_name("CodeMirror")
        script = "arguments[0].CodeMirror.setValue(`" + \
            self.source_code + "`);"
        self.driver.execute_script(
            script,
            code_mirror
        )

        button = self.driver.find_element_by_xpath(
            '//button[@type="submit"]')
        self.driver.execute_script('arguments[0].click()', button)

    def fetch_submission_id(self):
        return self.driver.current_url.split('/')[-1]

    def get_submission_verdict(self, submission_id, oj_problem_code):
        try:
            url = self.base_url + 'submission/' + str(submission_id)
            self.driver.get(url)
            progress_bar = self.driver.find_element_by_id(
                'progressbar_text_' + str(submission_id))

            score_text = progress_bar.get_attribute('innerText')
            if ('queue' in score_text) or ('Queue' in score_text) or len(score_text) == 0 or ('Compiling' in score_text) or ('Evaluating' in score_text):
                return {
                    'verdict': score_text,
                    'status': 'Pending'
                }
            elif 'error' in score_text:
                return {
                    'verdict': 'Compilation Error',
                    'status': 'Rejected'
                }

            your_score = int(score_text.split('/')[0])
            subtasks_div = self.driver.find_element_by_id('submission_details')
            subtask_detail_div = subtasks_div.find_elements_by_xpath('.//*')
            subtask_results = []
            id = 1
            for subtask in subtask_detail_div:
                try:
                    subtask_div = subtask.find_element_by_class_name(
                        'panel-title')
                    raw = subtask_div.get_attribute('innerText')
                    raw = raw.strip()
                    raw = raw.strip('Subtask #')
                    raw = raw.split('/')[0].strip()
                    subtask_id, score = map(float, raw.split('\n'))
                    verdict = ''
                    if score != 0:
                        verdict = 'Accepted'
                    else:
                        failed = subtask.find_element_by_class_name(
                            'danger').find_elements_by_tag_name('td')[1]
                        verdict = failed.get_attribute('innerText')
                    if subtask_id == id:
                        id += 1
                        subtask_results.append({
                            'subtask_id': int(subtask_id),
                            'score': score,
                            'verdict': verdict
                        })
                except:
                    pass
            subtask_results = json.dumps(subtask_results)
            if your_score == 100:
                return {
                    'verdict': 'Accepted',
                    'status': 'Accepted',
                    'score': your_score,
                    'subtask_results': subtask_results,
                }
            else:
                return {
                    'verdict': 'Partial Points',
                    'status': 'Rejected',
                    'score': your_score,
                    'subtask_results': subtask_results,
                }
        except Exception as e:
            return {
                'verdict': 'Error',
                'status': 'Error',
                'score': 0,
                'subtask_results': []
            }
            print(e)
