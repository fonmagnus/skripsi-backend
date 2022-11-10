from django.db.models import Q
from root.modules.problems.models import OJProblem, OJProblemForContest, OJSubmission, Problemset, ProblemsetEligibility, Team, TeamForProblemset, ProblemTag
from root.modules.accounts.models import UserAccount
from django.db.models import Q
from datetime import datetime
import re
import math
import unidecode
from datetime import datetime
from .BaseDbAccessor import BaseDbAccessor


class ProblemsetDbAccessorImpl(BaseDbAccessor):

    def get_all_published_problemset(self):
        return Problemset.objects.filter(
            Q(is_published=True)
        ).order_by('-priority_index', '-start_at')

    def get_all_oj_problems(self, request):
        oj_problems = OJProblem.objects.all()

        difficulty_from = int(request.get('difficulty_from', 0))
        difficulty_to = int(request.get('difficulty_to', 3500))
        oj_names = request.getlist('oj_names[]', [])

        oj_problems = oj_problems.filter(
            difficulty__gte=difficulty_from, difficulty__lte=difficulty_to
        )

        print(oj_names)

        if len(oj_names) > 0:
            oj_problems = oj_problems.filter(
                oj_name__in=oj_names
            )

        return {
            'result': super().do_query(oj_problems, request),
            'meta': {
                'total_items': oj_problems.count(),
                'total_page': math.ceil(oj_problems.count() / self.limit)
            }
        }

    def get_my_published_problemset(self, me):
        return Problemset.objects.filter(
            Q(created_by=me)
        ).order_by('-priority_index', '-is_active')

    def get_problemset_by_slug(self, slug):
        return Problemset.objects.get(slug=slug, is_active=True)

    def toggle(self, slug):
        problemset = Problemset.objects.get(slug=slug)
        problemset.is_active = not problemset.is_active
        problemset.save()
        return problemset

    def create_new_problemset(self, problemset_dict, user):
        slug = self.__get_problemset_slug_from_title(
            problemset_dict.get('title'))
        start_date = problemset_dict.get('start_date')
        start_time = problemset_dict.get('start_time')
        start_at = datetime.fromisoformat(start_date + " " + start_time)
        enable_partial_scoring = problemset_dict.get(
            'enable_partial_scoring', False)

        problemset = Problemset.objects.create(
            title=problemset_dict.get('title'),
            slug=slug,
            description='',
            start_at=start_at,
            duration_seconds=int(problemset_dict.get('duration')),
            is_published=(user.role == 'Admin'),
            is_active=True,
            greetings='',
            type=Problemset.Type.FULL_CODING,
            priority_index=0,
            is_leaderboard_enabled=True,
            is_public_leaderboard_enabled=False,
            created_by=user,
            enable_partial_scoring=enable_partial_scoring,
        )

        self.add_oj_problems_to_problemset(
            problemset, problemset_dict.get('problems'))
        self.add_eligible_users_to_problemset(
            problemset, problemset_dict.get('eligible_participants'), user)

        return problemset

    def update_problemset(self, problems_dict, user, slug):
        problemset = Problemset.objects.get(slug=slug)
        current_problems = OJProblemForContest.objects.filter(
            problemset=problemset)
        current_problems.delete()
        problems = problems_dict.get('problems')
        for problem in problems:
            new_oj_problem = problem.get('oj_problem')
            oj_name = new_oj_problem.get('oj_name')
            oj_problem_code = new_oj_problem.get('oj_problem_code')
            oj_problem = OJProblem.objects.get(Q(oj_name=oj_name) & (
                Q(oj_problem_code=oj_problem_code) | Q(oj_problem_code=oj_problem_code.upper())))
            OJProblemForContest.objects.create(
                problemset=problemset, oj_problem=oj_problem)
        return problemset

    def remove_oj_problem_for_contest(self, slug, oj_name, oj_problem_code):
        oj_problem_for_contest = OJProblemForContest.objects.get(problemset__slug=slug, oj_problem__oj_name=oj_name,
                                                                 oj_problem__oj_problem_code=oj_problem_code)
        return oj_problem_for_contest.delete()

    def get_submissions(self, slug, type):
        return OJSubmission.objects.filter(
            problemset__slug=slug
        ).order_by('id')

    def get_my_submissions(self, slug, my_user_id, type):
        return OJSubmission.objects.filter(
            problemset__slug=slug,
            user__id=my_user_id,
        ).order_by('-submitted_at')

    def get_problemset_slugs(self):
        return [problemset.slug for problemset in Problemset.objects.all()]

    def unset_user_eligibility(self, user_id, slug):
        p = ProblemsetEligibility.objects.filter(
            user__id=user_id, problemset__slug=slug, is_eligible=True)
        for _p in p:
            _p.is_eligible = False
            _p.save()

        return p.first()

    def get_eligible_users_in_problemset(self, slug):
        users = ProblemsetEligibility.objects.filter(
            is_eligible=True, problemset__slug=slug).values('user')
        print("Eligible Users in problemset {} :".format(slug), users)
        return [u['user'] for u in users]

    def get_all_users_in_problemset(self, slug):
        users = ProblemsetEligibility.objects.filter(
            problemset__slug=slug).values('user')
        return [u['user'] for u in users]

    def get_oj_submissions_from_users(self, users, slug):
        return OJSubmission.objects.filter(
            problemset__slug=slug,
            user__id__in=users)

    def get_oj_problem(self, oj_name, oj_problem_code):
        try:
            return OJProblem.objects.get(Q(oj_name=oj_name) & (Q(oj_problem_code=oj_problem_code) | Q(oj_problem_code=oj_problem_code.upper())))
        except OJProblem.DoesNotExist:
            return None

    def save_oj_problem(self, oj_problem_dict):
        oj_name = oj_problem_dict.get('oj_name')
        oj_problem_code = oj_problem_dict.get('oj_problem_code')
        oj_problem = OJProblem.objects.filter(
            oj_name=oj_name,
            oj_problem_code=oj_problem_code
        )

        raw_tags = oj_problem_dict.get('tags', [])
        tags = []
        for raw_tag in raw_tags:
            if raw_tag[0] == '*':
                continue
            tag = ProblemTag.objects.filter(name=raw_tag)
            if tag.exists():
                tag = tag.first()
            else:
                tag = ProblemTag.objects.create(name=raw_tag)
            tags.append(tag.id)

        if oj_problem.exists():
            oj_problem = oj_problem.first()
            oj_problem.title = oj_problem_dict.get('title')
            oj_problem.body = oj_problem_dict.get('body')
            oj_problem.time_limit = oj_problem_dict.get('time_limit')
            oj_problem.memory_limit = oj_problem_dict.get('memory_limit')
            oj_problem.difficulty = oj_problem_dict.get('difficulty')
            oj_problem.tags.set(tags)
            oj_problem.save()
            return oj_problem

        oj_problem = OJProblem.objects.create(
            oj_name=oj_problem_dict.get('oj_name'),
            oj_problem_code=oj_problem_dict.get('oj_problem_code'),
            url=oj_problem_dict.get('url'),
            title=oj_problem_dict.get('title'),
            body=oj_problem_dict.get('body'),
            time_limit=oj_problem_dict.get('time_limit'),
            memory_limit=oj_problem_dict.get('memory_limit'),
            difficulty=oj_problem_dict.get('difficulty', 0),
        )
        oj_problem.tags.set(tags)
        oj_problem.save()

        return oj_problem

    def save_oj_submission(self, oj_name, oj_problem_code, submission_id, verdict, user_id, source_code, problemset=None):
        user = UserAccount.objects.get(id=user_id)
        oj_submission = OJSubmission.objects.filter(
            user__id=user_id, submission_id=submission_id, oj_name=oj_name, oj_problem_code=oj_problem_code)
        if oj_submission.exists():
            oj_submission = oj_submission.first()
            if problemset is not None:
                oj_submission.problemset = problemset
            oj_submission.verdict = verdict
            oj_submission.save()

    def get_oj_submissions_history(self, oj_name, oj_problem_code, user_ids, problemset=None):
        result = OJSubmission.objects.filter(
            oj_name=oj_name, oj_problem_code=oj_problem_code, user__id__in=user_ids).order_by('-submitted_at')
        if problemset is not None:
            result = result.filter(problemset=problemset)
        return result

    def get_all_oj_submissions_history(self, oj_name, oj_problem_code, problemset=None):
        result = OJSubmission.objects.filter(
            oj_name=oj_name, oj_problem_code=oj_problem_code
        ).order_by('-submitted_at')

        if problemset is not None:
            result = result.filter(problemset=problemset)
        return result

    def get_oj_submission_verdict(self, oj_name, oj_problem_code, submission_id):
        try:
            return OJSubmission.objects.get(oj_name=oj_name, oj_problem_code=oj_problem_code, submission_id=submission_id)
        except OJSubmission.DoesNotExist:
            return OJSubmission.objects.get(id=submission_id)

    def get_oj_submission_detail(self, id):
        return OJSubmission.objects.get(id=id)

    def get_all_oj_problems_from_problemset(self, slug):
        return OJProblemForContest.objects.filter(problemset__slug=slug).order_by('priority_index')

    def register_contest(self, user, slug):
        problemset = Problemset.objects.get(slug=slug)
        eligibility = ProblemsetEligibility.objects.filter(
            user=user, problemset=problemset)
        if not eligibility.exists():
            return ProblemsetEligibility.objects.create(user=user, problemset=problemset, is_eligible=False)
        return eligibility.first()

    def add_oj_problems_to_problemset(self, problemset, problems_dict):
        index = 1
        for problem_dict in problems_dict:
            oj_problem_dict = problem_dict.get('oj_problem')
            oj_problem = OJProblem.objects.get(
                oj_name=oj_problem_dict.get('oj_name'),
                oj_problem_code=oj_problem_dict.get('oj_problem_code')
            )

            OJProblemForContest.objects.create(
                problemset=problemset,
                oj_problem=oj_problem,
                priority_index=index
            )

            index += 1

    def add_eligible_users_to_problemset(self, problemset, eligible_users, user):
        eligible_users = eligible_users.split()
        eligible_users.append(user.email)
        admins = UserAccount.objects.filter(role='Admin')
        for admin in admins:
            eligible_users.append(admin.email)

        for email in eligible_users:
            user = UserAccount.objects.get(email=email)
            ProblemsetEligibility.objects.create(
                problemset=problemset,
                user=user,
                is_eligible=True
            )

    def get_participants_for_contest(self, slug):
        return ProblemsetEligibility.objects.filter(problemset__slug=slug).exclude(user__role='Admin').order_by('is_eligible', 'user__name')

    def update_participant_status(self, problemset_eligibility_id, value, admin):
        problemset_eligbility = ProblemsetEligibility.objects.get(
            id=problemset_eligibility_id)

        problemset_eligbility.is_eligible = value
        problemset_eligbility.admitted_by = admin
        problemset_eligbility.save()
        return problemset_eligbility

    def get_teams_from_problemset(self, problemset):
        return TeamForProblemset.objects.filter(problemset=problemset)

    def get_user_team_in_problemset(self, user, problemset):
        return TeamForProblemset.objects.filter(
            problemset=problemset,
            team__members__in=[user]
        ).first()

    def register_team_members(self, team_name, emails):
        members = []
        for email in emails:
            members.append(UserAccount.objects.get(email=email))
        team = Team.objects.create(name=team_name)
        team.members.set(members)
        team.save()
        return team

    def register_team_for_contest(self, team_id, slug):
        team = Team.objects.get(id=team_id)
        problemset = Problemset.objects.get(slug=slug)
        for member in team.members.all():
            pe = ProblemsetEligibility.objects.filter(
                user__email=member.email)
            if not pe.exists():
                ProblemsetEligibility.objects.create(
                    problemset=problemset,
                    user=member
                )
        return TeamForProblemset.objects.create(
            team=team,
            problemset=problemset
        )

    def get_my_teams(self, user):
        return Team.objects.filter(members__in=[user])

    def get_team_members_from_team_id(self, team_id):
        return Team.objects.get(id=team_id).members.all()

    # ***
    # * private methods below
    # ***

    def __get_problemset_slug_from_title(self, title):
        slug = self.__slugify(title)
        existing_slugs = Problemset.objects.filter(slug__contains=slug)
        slug_cnt = len(existing_slugs)
        if slug_cnt == 0:
            return slug
        return slug + '-' + str(slug_cnt+1)

    def __slugify(self, text):
        text = unidecode.unidecode(text).lower()
        return re.sub(r'[\W_]+', '-', text).strip('-')
