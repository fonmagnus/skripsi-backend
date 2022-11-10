import requests
from bs4 import BeautifulSoup
import re


class OjUzScraper:
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://oj.uz/problem/view/'

    def scrap(self, oj_problem_code):
        self.url = self.base_url + oj_problem_code
        self.oj_problem_code = oj_problem_code

        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "html.parser")
        return self.get_dict(soup)

    def get_dict(self, soup):
        problemset_title = soup.find(class_='problem-title').get_text().strip()
        problemset_title = problemset_title.rstrip(
            'Compilation commands')
        problemset_title = problemset_title.rstrip()
        problemset_title = problemset_title.rstrip('Batch')
        problemset_title = problemset_title.rstrip('Interactive')
        problemset_title = problemset_title.rstrip('Output only')
        problemset_title = problemset_title.rstrip()

        src = soup.find(id='problem_statement_pdf').find('a').get('href')
        body = '<div style="display: flex; justify-content: center; align-items: center;"><object style="width: 100%; min-width: 50vw; height: 72vh;" data="' + src + '" type="application/pdf">' + \
            '<embed src="' + src + '" type="application/pdf" />' + '</object></div>'

        difficulty = 0

        constraints = soup.find('table', class_='table')
        tds = constraints.find_all('td')
        for td in tds:
            text = td.get_text()
            if 'ms' in text:
                time_limit = text
            if 'MiB' in text:
                memory_limit = text

        input_format = ''
        output_format = ''
        example = ''
        notes = ''
        result = {
            'oj_name': 'OjUz',
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
            'difficulty': difficulty,
        }

        return result

    # * PRIVATE METHODS
