from root.modules.webdriver.models import CrawlRequest
from root.modules.problems.models import OJSubmission


class WebdriverDbAccessor:
    def get_crawl_request_by_id(self, crawl_request_id):
        return CrawlRequest.objects.get(id=crawl_request_id)

    def get_oj_submission_verdict(self, oj_name, oj_problem_code, submission_id):
        return OJSubmission.objects.get(
            oj_name=oj_name,
            oj_problem_code=oj_problem_code,
            submission_id=submission_id
        )
