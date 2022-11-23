from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

import time
from root.modules.webdriver.models import OJLoginAccountInfo, CrawlRequest
from root.modules.problems.models import OJSubmission
import threading
from datetime import datetime


class GymWebdriver:
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://codeforces.com/'
        self.driver = kwargs.get('driver')

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass

    def submit_solution(self, oj_name, oj_problem_code, source_code, user_id, driver, problemset=None):
        self.driver = driver
        contest_id, problem_no = oj_problem_code[:-1], oj_problem_code[-1:]
        self.url = self.base_url + 'gym/' + \
            str(contest_id) + '/problem/' + problem_no
        self.contest_id = str(contest_id)
        self.problem_no = problem_no
        self.lang = "GNU G++17 7.3.0"
        self.source_code = source_code

        login_account = OJLoginAccountInfo.objects.filter(
            oj_name='Codeforces').order_by('?').first()

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
                oj_submission.save()

                if verdict.get('status') != 'Pending':
                    break
        except Exception as e:
            oj_submission.verdict = 'Error'
            oj_submission.save()
            print(e)

        self.driver.quit()

    def do_login(self, login_account):
        login_link = self.driver.find_element_by_link_text('Enter').click()
        self.driver.find_element_by_id(
            'handleOrEmail').send_keys(login_account.email_or_username)
        self.driver.find_element_by_id(
            'password').send_keys(login_account.password)
        self.driver.find_element_by_class_name(
            'submit').click()
        login_account.last_login = datetime.now()
        login_account.save()
        print('[LOGIN SUCCESS]')

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

        if not self.driver.find_element_by_id('toggleEditorCheckbox').is_selected():
            self.driver.find_element_by_id('toggleEditorCheckbox').click()
        code_editor = self.driver.find_element_by_id(
            'sourceCodeTextarea').send_keys(self.source_code)
        if self.driver.find_element_by_id('toggleEditorCheckbox').is_selected():
            self.driver.find_element_by_id('toggleEditorCheckbox').click()
        self.driver.find_element_by_class_name(
            'submit').click()

    def fetch_submission_id(self):
        return self.driver.find_element_by_class_name('id-cell').get_attribute('innerText')

    def get_submission_verdict(self, submission_id, oj_problem_code, driver):
        self.driver = driver
        crawl_request = CrawlRequest.objects.get(
            oj_name='Gym', submission_id=submission_id)
        login_account = crawl_request.oj_login_account_info
        self.driver.get(self.base_url)
        self.do_login(login_account)
        time.sleep(4)
        contest_id = oj_problem_code[:-1]
        submission_url = self.base_url + 'gym/' + \
            contest_id + '/submission/' + submission_id
        self.driver.get(submission_url)
        try:
            is_pending_verdict = self.driver.find_element_by_class_name(
                'verdict-waiting')
            verdict = is_pending_verdict.get_attribute('innerText')
            return {
                'verdict': verdict,
                'status': 'Pending'
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
                        'status': 'Rejected'
                    }
                except:
                    try:
                        is_partial_verdict = driver.find_elements_by_xpath(
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
                            is_partial_verdict = driver.find_elements_by_xpath(
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
