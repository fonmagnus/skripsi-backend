import requests
from bs4 import BeautifulSoup


class SpojScraper:
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://www.spoj.com/problems/'

    def scrap(self, oj_problem_code):
        self.url = self.base_url + oj_problem_code
        self.oj_problem_code = oj_problem_code

        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "html.parser")
        return self.get_dict(soup)

    def get_dict(self, soup):
        problemset_title = soup.find(
            id='problem-name').get_text().split('-')[1].strip()

        body = str(soup.find(id='problem-body'))

        constraints = soup.find(
            'table', id='problem-meta').findAll('tr')

        time_limit = ''
        memory_limit = ''
        for tr in constraints:
            if 'Time limit' in str(tr):
                time_limit = tr.get_text().lstrip('Time limit:').strip()
            elif 'Memory limit' in str(tr):
                memory_limit = tr.get_text().lstrip('Memory limit:').strip()

        input_format = ''
        output_format = ''
        example = ''
        notes = ''

        return {
            'oj_name': 'SPOJ',
            'oj_problem_code': self.oj_problem_code,
            'url': self.url,
            'title': problemset_title,
            'body': body,
            'time_limit': time_limit,
            'memory_limit': memory_limit,
            'input_format': input_format,
            'output_format': output_format,
            'example': example,
            'notes': notes,
        }
