from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
from root.modules.webdriver.models import OJLoginAccountInfo
from root.modules.webdriver.models import OJLoginAccountInfo, CrawlRequest
from root.modules.problems.models import OJSubmission
from datetime import datetime


class BaseWebdriver:
    def __init__(self, *args, **kwargs):
        opt = Options()
        if os.environ.get('ENV') == 'production':
            opt.add_argument('--headless')
            opt.add_argument('--disable-dev-shm-usage')
            opt.add_argument('--disable-gpu')
            opt.add_argument('--no-sandbox')
            opt.add_argument('--remote-debugging-port=9222')

        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=opt
        )

    def __del__(self):
        self.driver.quit()

    def mark_submission_error(self, oj_submission):
        self.driver.quit()
        oj_submission.verdict = 'Error'
        oj_submission.save()
        raise Exception('Server occured an error')

    # * returns all the required attributes from params
    def get_properties_from_param(self, params):
        return (
            params.get('oj_name', ""),
            params.get('oj_problem_code', ""),
            params.get('source_code', ""),
            params.get('user', None),
            params.get('problemset', None)
        )

    # * some pre work before submitting user solution to OJ
    def pre_submit_solution(self, params={}):
        (
            self.oj_name,
            self.oj_problem_code,
            self.source_code,
            self.user,
            self.problemset
        ) = self.get_properties_from_param(
            params
        )

        self.login_account = self.get_oj_login_account_info(
            self.oj_name, params)

        self.crawl_request = CrawlRequest.objects.create(
            oj_name=self.oj_name,
            oj_login_account_info=self.login_account
        )

        self.oj_submission = OJSubmission.objects.create(
            oj_name=self.oj_name,
            source_code=self.source_code,
            user=self.user,
            submission_id=None,
            verdict='Pending',
            oj_login_account_info=self.login_account,
            oj_problem_code=self.oj_problem_code,
            problemset=self.problemset
        )

    def get_oj_login_account_info(self, oj_name, params={}):
        return self.get_random_oj_account(oj_name)

    def post_successful_login(self):
        self.login_account.last_login = datetime.now()
        self.login_account.save()

    def get_random_oj_account(self, oj_name):
        return OJLoginAccountInfo.objects.filter(
            oj_name=oj_name
        ).order_by('?').first()
