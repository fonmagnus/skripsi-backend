from root.modules.accounts.models import UserAccount
from root.modules.problems.models import OJProblem, Team
from root.modules.problems.serializers import OJSubmissionSerializer
from root.repositories.ProblemsetDbAccessorImpl import ProblemsetDbAccessorImpl
from datetime import datetime
from django.utils import timezone, dateformat

import requests
import os
import json
import threading
from datetime import datetime
import time
import collections


class ProblemsetServiceImpl:

    def __init__(self, *args, **kwargs):
        self.db_accessor = ProblemsetDbAccessorImpl()
        self.webscraper_service = kwargs.get('webscraper_service')
        self.webdriver_service = kwargs.get('webdriver_service')

    def get_all_published_problemset(self):
        return self.db_accessor.get_all_published_problemset()

    def get_my_published_problemset(self, me):
        return self.db_accessor.get_my_published_problemset(me)

    def get_problemset_by_slug(self, slug):
        return self.db_accessor.get_problemset_by_slug(slug)

    def get_all_oj_problems(self, request):
        if request.get('oj_problem_code') and request.getlist('oj_names[]'):
            oj_names = request.getlist('oj_names[]')
            for oj_name in oj_names:
                self.get_oj_problem(oj_name, request.get('oj_problem_code'))
        
        result = self.db_accessor.get_all_oj_problems(request)
        return result

    def get_all_oj_submissions(self, request):
        result = self.db_accessor.get_all_oj_submissions(request)
        return result

    def toggle(self, slug):
        return self.db_accessor.toggle(slug)

    def create_new_problemset(self, problemset_dict, user):
        return self.db_accessor.create_new_problemset(problemset_dict, user)

    def update_problemset(self, problems_dict, user, slug):
        return self.db_accessor.update_problemset(problems_dict, user, slug)

    def remove_oj_problem_for_contest(self, slug, oj_name, oj_problem_code):
        return self.db_accessor.remove_oj_problem_for_contest(slug, oj_name, oj_problem_code)

    def get_submissions(self, slug, type):
        return self.db_accessor.get_submissions(slug, type)

    def get_my_submissions(self, slug, my_user_id, type):
        return self.db_accessor.get_my_submissions(slug, my_user_id, type)

    def get_problemset_slugs(self):
        return self.db_accessor.get_problemset_slugs()

    def unset_user_eligibility(self, user_id, slug):
        return self.db_accessor.unset_user_eligibility(user_id, slug)

    def get_eligible_users_in_problemset(self, slug):
        return self.db_accessor.get_eligible_users_in_problemset(slug)

    def get_all_users_in_problemset(self, slug):
        return self.db_accessor.get_all_users_in_problemset(slug)

    def get_contest_leaderboard(self, slug, user_id, only_show_mine=False):
        user = UserAccount.objects.get(id=user_id)
        problemset = self.db_accessor.get_problemset_by_slug(slug)

        users = [user.id]
        if (problemset.is_leaderboard_enabled or problemset.is_public_leaderboard_enabled or user.role == 'Admin') and not only_show_mine:
            users = self.get_all_users_in_problemset(slug)

        submissions = self.db_accessor.get_oj_submissions_from_users(
            users, slug)
        user_submission_per_problem = self.__get_user_submission_per_problem(
            submissions, problemset)
        user_points_per_problem = self.__get_user_points_per_problem(
            user_submission_per_problem, problemset)
        raw_leaderboard = self.__get_leaderboard(
            user_points_per_problem, problemset)
        leaderboard = self.__process_leaderboard(
            raw_leaderboard, problemset, user)
        return leaderboard

    def get_oj_problem(self, oj_name, oj_problem_code):
        oj_problem_code = oj_problem_code.strip()
        problem = self.db_accessor.get_oj_problem(oj_name, oj_problem_code)
        if problem == None:
            problem = self.webscraper_service.scrap(oj_name, oj_problem_code)
            problem = self.db_accessor.save_oj_problem(problem)
        return problem

    def submit_oj_problem(self, oj_name, oj_problem_code, source_code, user, problemset=None):
        crawl_request = self.webdriver_service.submit_solution(
            {
                'oj_name': oj_name,
                'oj_problem_code': oj_problem_code,
                'source_code': source_code,
                'user': user,
                'problemset': problemset
            }
        )
        return crawl_request

    def get_oj_submission_verdict(self, id):
        return self.db_accessor.get_oj_submission_verdict(id)

    def get_oj_submissions_history(self, oj_name, oj_problem_code, user_ids, problemset=None):
        submissions = self.db_accessor.get_oj_submissions_history(
            oj_name, oj_problem_code, user_ids, problemset)
        return submissions

    def get_all_oj_submissions_history(self, oj_name, oj_problem_code, user_id, problemset=None):
        submissions = self.db_accessor.get_all_oj_submissions_history(
            oj_name, oj_problem_code, problemset)
        return submissions

    def get_oj_submission_detail(self, id):
        return self.db_accessor.get_oj_submission_detail(id)

    def get_all_oj_problems_from_problemset(self, slug):
        return self.db_accessor.get_all_oj_problems_from_problemset(slug)

    def register_contest(self, user, slug):
        return self.db_accessor.register_contest(user, slug)

    def get_participants_for_contest(self, slug):
        return self.db_accessor.get_participants_for_contest(slug)

    def update_participant_status(self, problemset_eligibility_id, value, admin):
        return self.db_accessor.update_participant_status(problemset_eligibility_id, value, admin)

    def register_team_members(self, team_name, emails):
        return self.db_accessor.register_team_members(team_name, emails)

    def register_team_for_contest(self, team_id, slug):
        return self.db_accessor.register_team_for_contest(team_id, slug)

    def get_my_teams(self, user):
        return self.db_accessor.get_my_teams(user)

    def get_user_team_in_problemset(self, user, slug):
        problemset = self.db_accessor.get_problemset_by_slug(slug)
        return self.db_accessor.get_user_team_in_problemset(user, problemset)

    def get_team_members_from_team_id(self, team_id):
        return self.db_accessor.get_team_members_from_team_id(team_id)

    def get_comments_from_oj_problem(self, oj_name, oj_problem_code):
        return self.db_accessor.get_all_comments_from_oj_problem(oj_name, oj_problem_code)
    
    def post_comment_to_oj_problem(self, oj_problem, user, content):
        return self.db_accessor.post_comment_to_oj_problem(oj_problem, user, content)

    def get_user_oj_submissions_history(self, user, params={}):
        return self.db_accessor.get_user_oj_submission_history(user, params)

    def get_students_work(self, student, params):
        if params.get('oj_name') == 'Portal':
            response = self.get_user_oj_submissions_history(
                student, params)
            serializer = OJSubmissionSerializer(
                response.get('data'), many=True)
            return {
                'data': serializer.data,
                'metadata': response.get('metadata')
            }

    def get_all_oj_submissions_from_user(self, user):
        return self.db_accessor.get_all_oj_submissions_from_user(user)

    def get_user_statistics(self, user):
        submissions = self.get_all_oj_submissions_from_user(user)

        difficulty_statistics = {}
        tag_statistics = {}
        solved_problems = set()

        for submission in submissions:
            if submission.status != 'Accepted':
                continue
            solved_problems.add(submission.id)
            oj_problem = self.get_oj_problem(
                submission.oj_name, submission.oj_problem_code)
            difficulty = oj_problem.difficulty

            if difficulty is None:
                continue
            if not difficulty in difficulty_statistics:
                difficulty_statistics[difficulty] = 0
            difficulty_statistics[difficulty] += 1

            tags = oj_problem.tags.all()
            for tag in tags:
                if not tag in tag_statistics:
                    tag_statistics[tag.name] = 0
                tag_statistics[tag.name] += 1

        # * sort tags by frequencies
        tag_statistics = dict(
            sorted(tag_statistics.items(), key=lambda item: item[1], reverse=True))
        difficulty_statistics = collections.OrderedDict(
            sorted(difficulty_statistics.items()))

        difficulty_statistics = self.__reformat(difficulty_statistics)
        tag_statistics = self.__reformat(tag_statistics)
        return {
            'difficulty_statistics': difficulty_statistics,
            'tag_statistics': tag_statistics
        }

    def __reformat(self, statistics):
        result = []
        for key, value in statistics.items():
            result.append({
                'key': key,
                'value': value
            })
        return result

    # * private

    def __get_user_submission_per_problem(self, submissions, problemset):
        result = {}
        for s in submissions:
            key = (s.user.email, s.oj_problem_code)
            if problemset.enable_team_contest:
                team = s.user.email
                team_in_this_contest = self.db_accessor.get_user_team_in_problemset(
                    s.user, problemset)
                if team_in_this_contest is not None:
                    team = team_in_this_contest.team.id
                key = (team, s.oj_problem_code)
            value = {
                'verdict': s.verdict,
                'score': s.score,
                'submitted_at': s.submitted_at
            }
            if not key in result.keys():
                result[key] = [value]
            else:
                result[key].append(value)
        return result

    def __get_user_points_per_problem(self, user_submission_per_problem, problemset):
        result = {}

        for key in user_submission_per_problem.keys():
            submissions = user_submission_per_problem[key]
            is_accepted = False
            accepted_at = datetime.now()
            penalty = 0
            score = 0
            for s in submissions:
                if s.get('verdict') == 'Accepted':
                    is_accepted = True
                    accepted_at = s.get('submitted_at')
                elif 'runtime error' in s.get('verdict').lower() or \
                        'wrong answer' in s.get('verdict').lower() or \
                        'time limit' in s.get('verdict').lower() or\
                        'memory limit' in s.get('verdict').lower():
                    penalty += 20

                score = max(score, int(s.get('score', 0)))

            accepted_time = 0
            if is_accepted:
                if not problemset.enable_virtual_contest:
                    accepted_time = (accepted_at -
                                     problemset.start_at).total_seconds() // 60
                else:
                    email = key[0]
                    user = UserAccount.objects.get(email=email)
                    active_virtual_contest = self.db_accessor.get_user_virtual_contest(
                        user.id, problemset.slug)
                    accepted_time = (
                        accepted_at - active_virtual_contest.start_at).total_seconds() // 60
                penalty += accepted_time
            else:
                penalty = 0

            result[key] = {
                'is_accepted': is_accepted,
                'penalty': penalty,
                'score': score,
                'attempts': len(submissions),
                'accepted_at': accepted_time,
            }
        return result

    def __get_leaderboard(self, user_points_per_problem, problemset):
        result = {}
        for key in user_points_per_problem.keys():
            if not key[0] in result.keys():
                points = 1 if user_points_per_problem[key]['is_accepted'] else 0
                if problemset.enable_partial_scoring:
                    points = user_points_per_problem[key]['score']

                penalty = user_points_per_problem[key]['penalty']
                result[key[0]] = {
                    'total': points,
                    'penalty': penalty,
                    'submissions': {
                        key[1]: user_points_per_problem[key]
                    }
                }
            else:
                points = 1 if user_points_per_problem[key]['is_accepted'] else 0
                if problemset.enable_partial_scoring:
                    points = user_points_per_problem[key]['score']

                penalty = user_points_per_problem[key]['penalty']
                result[key[0]]['total'] += points
                result[key[0]]['penalty'] += penalty
                result[key[0]]['submissions'][key[1]
                                              ] = user_points_per_problem[key]
        return result

    def __process_leaderboard(self, leaderboard, problemset, user):
        result = []
        for l in leaderboard.keys():
            if problemset.enable_team_contest:
                if isinstance(l, str):
                    d = {'email': l, 'name': UserAccount.objects.get(
                        email=l).name}
                else:
                    d = {'email': l, 'name': Team.objects.get(id=l).name}
            else:
                d = {'email': l, 'name': UserAccount.objects.get(email=l).name}
            for k in leaderboard[l].keys():
                d[k] = leaderboard[l][k]

            if problemset.is_leaderboard_enabled or problemset.is_public_leaderboard_enabled or user.email == l or user.role == 'Admin':
                result.append(d)
        result.sort(key=lambda x: (-x['total'], x['penalty']))
        return result
