from root.modules.webdriver.helpers.webscrapers.AtcoderScraper import AtcoderScraper


class WebscraperService:
    def __init__(self, *args, **kwargs):
        self.atcoder_scraper = AtcoderScraper()

    def scrap(self, oj_name, oj_problem_code):
        if oj_name == 'Atcoder':
            return self.atcoder_scraper.scrap(oj_problem_code)
