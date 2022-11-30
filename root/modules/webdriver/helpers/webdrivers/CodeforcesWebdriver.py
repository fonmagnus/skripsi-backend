from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


import time
from root.modules.webdriver.models import OJLoginAccountInfo, CrawlRequest
from root.modules.problems.models import OJSubmission
from .BaseWebdriver import BaseWebdriver
import threading
from datetime import datetime


class CodeforcesWebdriver(BaseWebdriver):
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://codeforces.com/'
        BaseWebdriver.__init__(self, *args, **kwargs)

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass

    def submit_solution(self, params={}):
        self.pre_submit_solution(params)
        contest_id, problem_no = self.oj_problem_code[:-
                                                      1], self.oj_problem_code[-1:]
        if problem_no.isnumeric():
            contest_id, problem_no = self.oj_problem_code[:-
                                                          2], self.oj_problem_code[-2:]
        self.url = self.base_url + 'contest/' + \
            str(contest_id) + '/problem/' + problem_no
        self.contest_id = str(contest_id)
        self.problem_no = problem_no
        self.lang = "GNU G++17 7.3.0"
        self.source_code = self.source_code

        thread = threading.Thread(
            target=self.do_crawl,
            args=[self.oj_submission]
        )
        thread.setDaemon(True)
        thread.start()
        return self.crawl_request

    def do_crawl(self, oj_submission):
        self.driver.get(self.url)
        try:
            self.do_login()
            if not self.check_login_successful():
                self.do_login(reattempt=True)
            self.post_successful_login()

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
        except Exception as e:
            self.mark_submission_error(oj_submission)

        # time.sleep(200)

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

        self.driver.quit()

    def do_login(self, reattempt=False):
        if reattempt:
            self.login_account = self.get_random_oj_account(self.oj_name)

        login_link = self.driver.find_element_by_link_text('Enter').click()
        self.driver.find_element_by_id(
            'handleOrEmail').send_keys(self.login_account.email_or_username)
        self.driver.find_element_by_id(
            'password').send_keys(self.login_account.password)
        self.driver.find_element_by_class_name(
            'submit').click()

    def check_login_successful(self):
        try:
            time.sleep(4)
            submit_link = self.driver.find_elements_by_tag_name('a')
            for a in submit_link:
                text = a.get_attribute('innerHTML')
                if text == 'Submit Code':
                    return True
            return False
        except:
            print('Login with', self.login_account, 'failed')
            return False
        return True

    def do_submit(self):
        time.sleep(4)
        submit_link = self.driver.find_elements_by_tag_name('a')
        for a in submit_link:
            text = a.get_attribute('innerHTML')
            if text == 'Submit Code':
                a.click()
                break

        ddelement = Select(
            self.driver.find_element_by_name('submittedProblemIndex'))
        ddelement.select_by_value(self.problem_no)
        ddelement = Select(
            self.driver.find_element_by_name('programTypeId'))
        ddelement.select_by_visible_text(self.lang)

        self.driver.find_element_by_id('toggleEditorCheckbox').click()
        code_editor = self.driver.find_element_by_id(
            'sourceCodeTextarea').send_keys(self.source_code)
        self.driver.find_element_by_id('toggleEditorCheckbox').click()
        time.sleep(4)
        self.driver.find_element_by_class_name(
            'submit').click()

    def fetch_submission_id(self):
        time.sleep(3)
        return self.driver.find_element_by_class_name('id-cell').get_attribute('innerText')

    def get_submission_verdict(self, submission_id, oj_problem_code):
        contest_id, problem_no = oj_problem_code[:-1], oj_problem_code[-1:]
        if problem_no.isnumeric():
            contest_id, problem_no = oj_problem_code[:-2], oj_problem_code[-2:]
        submission_url = self.base_url + 'contest/' + \
            contest_id + '/submission/' + submission_id
        print(submission_url)
        self.driver.get(submission_url)
        try:
            is_pending_verdict = self.driver.find_element_by_class_name(
                'verdict-waiting')
            verdict = is_pending_verdict.get_attribute('innerText')
            return {
                'verdict': verdict,
                'status': 'Pending',
                'score': 0
            }
        except:
            try:
                is_accepted_verdict = self.driver.find_element_by_class_name(
                    'verdict-accepted')
                verdict = is_accepted_verdict.get_attribute('innerText')
                return {
                    'verdict': 'Accepted',
                    'status': 'Accepted',
                    'score': 100
                }
            except:
                try:
                    is_rejected_verdict = self.driver.find_element_by_class_name(
                        'verdict-rejected')
                    verdict = is_rejected_verdict.get_attribute('innerText')
                    return {
                        'verdict': verdict,
                        'status': 'Rejected',
                        'score': 0
                    }
                except:
                    try:
                        is_partial_verdict = self.driver.find_elements_by_xpath(
                            "//*[contains(text(), 'Perfect result')]")[0]
                        verdict = is_partial_verdict.get_attribute(
                            'innerText')
                        return {
                            'verdict': 'Accepted',
                            'status': 'Accepted',
                            'score': 100
                        }
                    except:
                        try:
                            is_partial_verdict = self.driver.find_elements_by_xpath(
                                "//*[contains(text(), 'Partial result')]")[0]
                            verdict, score = is_partial_verdict.get_attribute(
                                'innerText').split(': ')
                            score = score.strip(' points')
                            return {
                                'verdict': 'Partial points',
                                'status': 'Rejected',
                                'score': float(score)
                            }

                        except Exception as e:
                            print(e)
                            return {
                                'verdict': 'Compilation error',
                                'status': 'Rejected',
                                'score': 0
                            }
