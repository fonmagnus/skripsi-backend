import io
import json
import zipfile
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

import time
from root.modules.webdriver.models import OJLoginAccountInfo, CrawlRequest
from root.modules.problems.models import OJProblem, OJSubmission
import threading
from datetime import datetime
import os
import requests
from zipfile import ZipFile, ZIP_DEFLATED


class TLXWebdriver:
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://tlx.toki.id/'
        self.api_url = 'https://api.tlx.toki.id/v2/submissions/programming/id/'
        self.driver = kwargs.get('driver')

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass

    def submit_solution(self, oj_name, oj_problem_code, source_code, user_id, driver, problemset=None):
        self.driver = driver
        slug, problem_code = '-'.join(oj_problem_code.split('-')
                                      [:-1]), oj_problem_code.split('-')[-1]

        login_account = OJLoginAccountInfo.objects.filter(
            oj_name='TLX').order_by('?').first()

        crawl_request = CrawlRequest.objects.create(
            oj_name=oj_name, oj_login_account_info=login_account)

        oj_submission = OJSubmission.objects.create(
            oj_name=oj_name,
            source_code=source_code,
            user_id=user_id,
            submission_id=None,
            verdict='Pending',
            oj_problem_code=oj_problem_code,
            oj_login_account_info=login_account,
            problemset=problemset
        )

        self.url = self.base_url + 'problems/' + slug + '/' + problem_code
        self.lang = "C++17"
        self.source_code = source_code
        self.oj_problem = OJProblem.objects.get(
            oj_name=oj_name, oj_problem_code=oj_problem_code)

        ext = '.cpp'
        if self.oj_problem.type == 'output_only':
            ext = '.zip'
            self.filename = "TLX-" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ext
            with open(self.filename, 'wb') as file:
                file_content = self.source_code.read()
                file.write(file_content)

        thread = threading.Thread(target=self.do_crawl, args=[
                                  self.url, crawl_request, oj_name, source_code, user_id, oj_problem_code, login_account, oj_submission])
        thread.setDaemon(True)
        thread.start()
        return crawl_request

    def do_crawl(self, url, crawl_request, oj_name, source_code, user_id, oj_problem_code, login_account, oj_submission):
        try:
            self.driver.get(url)
            time.sleep(3)
            self.do_login(login_account)
            time.sleep(3)
            self.driver.get(url)
            self.do_submit()
            submission_id = self.fetch_submission_id(login_account)
            crawl_request.submission_id = submission_id
            crawl_request.status = 'Completed'
            crawl_request.save()
            oj_submission.submission_id = submission_id
            oj_submission.save()
            thread = threading.Thread(
                target=self.keep_fetching_verdict, args=[oj_submission])
            thread.setDaemon(True)
            thread.start()
        except Exception as e:
            oj_submission.verdict = 'Error'
            oj_submission.save()
            print(e)
            self.driver.quit()

    def keep_fetching_verdict(self, oj_submission):
        try:
            while True:
                time.sleep(2)
                self.driver.refresh()
                verdict = self.get_submission_verdict(
                    oj_submission.submission_id, oj_submission.oj_problem_code, self.driver)

                oj_submission.verdict = verdict.get('verdict')
                oj_submission.status = verdict.get('status')
                oj_submission.score = verdict.get('score', 0)
                oj_submission.subtask_results = verdict.get('subtask_results')
                oj_submission.save()

                if verdict.get('status') != 'Pending':
                    break
        except Exception as e:
            oj_submission.verdict = 'Error'
            oj_submission.save()
            print(e)

        self.driver.quit()

    def do_login(self, login_account):
        login_link = self.driver.find_element_by_link_text('Log in')
        self.driver.execute_script('arguments[0].click()', login_link)
        self.driver.find_element_by_name(
            'usernameOrEmail').send_keys(login_account.email_or_username)
        self.driver.find_element_by_name(
            'password').send_keys(login_account.password)
        login_button = self.driver.find_element_by_xpath(
            '//button[normalize-space()="Log in"]')
        self.driver.execute_script('arguments[0].click()', login_button)
        login_account.last_login = datetime.now()
        login_account.save()

    def do_submit(self):
        time.sleep(2)
        submission_config = self.driver.find_element_by_class_name(
            'programming-problem-submission-form__tablde')

        if isinstance(self.source_code, str):
            button = submission_config.find_element_by_tag_name('button')
            self.driver.execute_script('arguments[0].click()', button)
            lang_choice = self.driver.find_element_by_xpath(
                '//div[normalize-space()="C++11"]')
            self.driver.execute_script('arguments[0].click()', lang_choice)
            self.filename = "TLX-" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".cpp"
            f = open(self.filename, "w")
            f.write(self.source_code)
            f.close()

        uploader = self.driver.find_element_by_name('sourceFiles.source')
        uploader.send_keys(os.getcwd() + "/" + self.filename)
        time.sleep(1)
        submit_button = self.driver.find_element_by_xpath(
            '//button[normalize-space()="Submit"]')
        self.driver.execute_script('arguments[0].click()', submit_button)

        time.sleep(1)
        os.remove(self.filename)

    def fetch_submission_id(self, login_account):
        time.sleep(2)
        table = self.driver.find_element_by_class_name('submissions-table')
        tbody = table.find_element_by_tag_name('tbody')
        tr = tbody.find_element_by_tag_name('tr')
        td = tr.find_element_by_tag_name('td').get_attribute('innerText')
        return td

    def get_submission_verdict(self, submission_id, oj_problem_code, driver):
        try:
            self.driver = driver
            crawl_request = CrawlRequest.objects.get(
                oj_name='TLX', submission_id=submission_id)
            url = self.api_url + submission_id
            print(url)

            response = requests.get(url).json()
            status_text = response.get('data').get('submission').get(
                'latestGrading').get('verdict').get('code')

            if status_text == '?':
                return {
                    'verdict': 'Running',
                    'status': 'Pending',
                }

            score = response.get('data').get('submission').get(
                'latestGrading').get('score')
            print('score', score)

            subtask_results_raw = response.get('data').get('submission').get(
                'latestGrading').get('details').get('subtaskResults')
            subtask_results = []

            for subtask in subtask_results_raw:
                subtask_id = subtask.get('id')
                verdict = subtask.get('verdict').get('code')

                if verdict == 'AC':
                    verdict = 'Accepted'
                elif verdict == 'WA':
                    verdict = 'Wrong Answer'
                elif verdict == 'TLE':
                    verdict = 'Time Limit Exceeded'
                elif verdict == 'CE':
                    verdict = 'Compile Error'
                elif verdict == 'RTE':
                    verdict = 'Runtime Error'
                elif verdict == 'MLE':
                    verdict = 'Memory Limit Exceeded'

                subtask_score = subtask.get('score')
                subtask_results.append({
                    'subtask_id': subtask_id,
                    'verdict': verdict,
                    'score': subtask_score
                })

            subtask_results = json.dumps(subtask_results)

            if status_text == 'AC':
                return {
                    'verdict': 'Accepted',
                    'status': 'Accepted',
                    'score': 100,
                    'subtask_results': subtask_results,
                }
            elif status_text == '?':
                return {
                    'verdict': 'Running',
                    'status': 'Pending',
                }
            else:
                if status_text == 'WA':
                    status_text = 'Wrong Answer'
                elif status_text == 'TLE':
                    status_text = 'Time Limit Exceeded'
                elif status_text == 'CE':
                    status_text = 'Compile Error'
                elif status_text == 'RTE':
                    status_text = 'Runtime Error'
                elif status_text == 'MLE':
                    status_text = 'Memory Limit Exceeded'

                return {
                    'verdict': status_text,
                    'status': 'Rejected',
                    'score': score,
                    'subtask_results': subtask_results,
                }
        except Exception as e:
            self.driver.quit()
            raise(e)
            pass
