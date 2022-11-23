# to run script :
# exec(open('script/codeforces_difficulty_fetcher.py').read())
import requests
from root.services import problemset_service
from root.modules.problems.models import OJProblem

url = 'https://codeforces.com/api/problemset.problems'
response = requests.get(url).json().get('result').get('problems')

for problem in response:
    contest_id = problem.get('contestId')
    alias = problem.get('index')
    problem_code = f'{contest_id}{alias}'
    problem_title = problem.get('name')
    difficulty = problem.get('rating')

    try:
        oj_problem = problemset_service.get_oj_problem(
            'Codeforces', problem_code)
        oj_problem.difficulty = difficulty
        oj_problem.save()
        print(problem_code, problem_title, difficulty)
    except Exception as e:
        print(e)
        print('Failed to scrap', problem_code)
