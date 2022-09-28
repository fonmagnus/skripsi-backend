import requests
from bs4 import BeautifulSoup
import re


class AtcoderScraper:
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://atcoder.jp/contests/'

    def scrap(self, oj_problem_code):
        contest_id = oj_problem_code.split('_')[0]
        self.url = self.base_url + \
            str(contest_id) + '/tasks/' + oj_problem_code
        self.oj_problem_code = oj_problem_code

        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "html.parser")
        return self.get_dict(soup)

    def get_dict(self, soup):
        problemset_title = soup.find('span', class_='h2').get_text(
        ).strip().rstrip('Editorial').split('-')[-1].strip()

        body = soup.find(class_='lang-en')
        for span in body.find_all("span", {'class': 'btn'}):
            span.decompose()

        try:
            difficulty = str(list(body)[1].find('var')).lstrip(
                '<var>').rstrip('</var>')
            raw_difficulty = difficulty
            difficulty = self.__normalize_difficulty(float(difficulty))
        except Exception as e:
            difficulty = 0

        if 'Score' in str(list(body)[1]):
            body = ''.join(map(str, list(body)[3:]))
        else:
            body = ''.join(map(str, list(body)[1:]))

        constraints = soup.find('p', text=re.compile(
            'Time Limit*')).get_text().strip()
        time_limit = constraints.split(' / ')[0].lstrip('Time Limit: ')
        memory_limit = constraints.split(' / ')[1].lstrip('Memory Limit: ')

        io_format = soup.find(class_='lang-en').find(class_='io-style')
        input_format = str(list(io_format.findAll(class_='part'))[0])
        output_format = str(list(io_format.findAll(class_='part'))[1])
        example = ''
        notes = ''

        return {
            'oj_name': 'Atcoder',
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
            'raw_difficulty': raw_difficulty,
        }

    # * PRIVATE METHODS
    def __normalize_difficulty(self, difficulty):
        ATCODER_MIN_DIFFICULTY = 50
        ATCODER_MAX_DIFFICULTY = 1600
        constant_scale = (ATCODER_MAX_DIFFICULTY -
                          ATCODER_MIN_DIFFICULTY) / 9
        return (difficulty - ATCODER_MIN_DIFFICULTY) / constant_scale + 1.5
