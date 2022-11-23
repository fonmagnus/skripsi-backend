# to run script :
# exec(open('script/atcoder_difficulty_fetcher.py').read())
import requests
from root.services import problemset_service
from root.modules.problems.models import OJProblem

url = 'https://kenkoooo.com/atcoder/resources/problem-models.json'
response = requests.get(url).json()

for problem in response.keys():
    value = response.get(problem)
    difficulty = value.get('difficulty', 800)
    difficulty = (difficulty // 100) * 100
    if difficulty <= 800:
        difficulty = 800
    if difficulty > 3500:
        difficulty = 3500
    try:
        oj_problem = problemset_service.get_oj_problem('Atcoder', problem)
        oj_problem.difficulty = difficulty
        oj_problem.save()
        print(oj_problem.oj_problem_code,
              oj_problem.title, oj_problem.difficulty)
    except Exception as e:
        print('Failed to scrap', problem)
