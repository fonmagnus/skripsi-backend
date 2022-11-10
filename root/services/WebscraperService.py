from root.modules.webdriver.helpers.webscrapers.AtcoderScraper import AtcoderScraper
from root.modules.webdriver.helpers.webscrapers.CodeforcesScraper import CodeforcesScraper
from root.modules.webdriver.helpers.webscrapers.TLXScraper import TLXScraper
from root.modules.webdriver.helpers.webscrapers.OjUzScraper import OjUzScraper
from root.modules.webdriver.helpers.webscrapers.GymScraper import GymScraper


class WebscraperService:
    def __init__(self, *args, **kwargs):
        self.scraper = {
            'Atcoder': AtcoderScraper(),
            'Codeforces': CodeforcesScraper(),
            'TLX': TLXScraper(),
            'Gym': GymScraper(),
            'OjUz': OjUzScraper()
        }

    def scrap(self, oj_name, oj_problem_code):
        scraper = self.scraper.get(oj_name)
        return scraper.scrap(oj_problem_code)
