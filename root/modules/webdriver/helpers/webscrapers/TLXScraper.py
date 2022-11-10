import requests


class TLXScraper:
    def __init__(self, *args, **kwargs):
        self.base_url = 'https://tlx.toki.id/problems/'
        self.api_url = 'https://api.tlx.toki.id/v2/problemsets/'

    def scrap(self, oj_problem_code):
        slug, problem_code = '-'.join(oj_problem_code.split('-')
                                      [:-1]), oj_problem_code.split('-')[-1]
        self.url = self.base_url + slug + '/' + problem_code.upper()
        self.oj_problem_code = oj_problem_code

        request_url = self.api_url + 'slug/' + slug
        response = requests.get(request_url).json()
        jid = response.get('jid')

        request_url = self.api_url + jid + '/problems/' + \
            problem_code + '/worksheet?language=id'
        response = requests.get(request_url).json()
        return self.get_dict(response.get('worksheet'))

    def get_dict(self, response):
        problemset_title = response.get('statement').get('title')
        body = response.get('statement').get('text')
        time_limit = str(response.get('limits').get(
            'timeLimit') / 1000) + ' seconds'
        memory_limit = str(response.get(
            'limits').get('memoryLimit')) + ' bytes'
        type = str(response.get('submissionConfig').get('gradingEngine'))

        if type == 'OutputOnly':
            type = 'output_only'
        elif 'Interactive' in type:
            type = 'interactive'
        else:
            type = 'batch'

        input_format = ''
        output_format = ''
        example = ''
        notes = ''

        return {
            'oj_name': 'TLX',
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
            'type': type
        }
