# to run script use exec(open('script/scrap_oj_problems.py').read())
from root.services import problemset_service
import time
from random import randint

oj_names = [
    # 'Atcoder',
    'Codeforces',
]

limit = {
    'Atcoder': {
        'abc': (42, 226),
        'arc': (58, 129),
        'agc': (1, 56),
    },
    'Codeforces': {
        '': (1, 1754)
    }
}

for oj_name in oj_names:
    contests = ['']
    if oj_name == 'Atcoder':
        contests = ['abc', 'arc', 'agc']

    for contest in contests:
        oj_problem_code_base = contest
        for id in range(limit[oj_name][contest][0], limit[oj_name][contest][1]):
            oj_problem_code_id = oj_problem_code_base
            if oj_name == 'Atcoder':
                if id < 10:
                    oj_problem_code_id += '00'
                elif id < 100:
                    oj_problem_code_id += '0'
            oj_problem_code_id += str(id)

            for alph in range(ord('A'), ord('I')):
                oj_problem_code = oj_problem_code_id
                if oj_name == 'Atcoder':
                    oj_problem_code += '_' + chr(alph - ord('A') + ord('a'))
                else:
                    oj_problem_code += chr(alph)

                print(oj_name, oj_problem_code)
                try:
                    sleeper = 0
                    if oj_name == 'Codeforces':
                        sleeper = randint(1, 10)
                    time.sleep(sleeper)
                    res = problemset_service.get_oj_problem(
                        oj_name, oj_problem_code)
                    print(res)
                except Exception as e:
                    print(e)
