from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django.http import JsonResponse

from root.modules.problems.serializers import (
    BodylessOJProblemForContestSerializer,
    OJSubmissionSerializer,
    OJSubmissionDetailSerializer,
    ProblemsetSerializer,
    OJProblemSerializer,
    TeamForProblemsetSerializer,
    TeamSerializer,
    OJProblemForContestSerializer,
    ProblemsetEligibilitySerializer,
)

from root.modules.webdriver.serializers import (
    CrawlRequestSerializer
)

from root.modules.problems.permissions import (
    IsEligibleWorkingOnProblemset,
    IsOJSubmissionOwner,
    IsProblemsetOwner,
)

from root.services import (
    problemset_service,
    webdriver_service,
    account_service,
)

import root.modules.accounts.utils as utils
from root.modules.accounts.serializers import UserSerializer
from root.modules.accounts.permissions import IsAdminRole


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_problems(request):
    problemsets = problemset_service.get_all_published_problemset()
    serializer = ProblemsetSerializer(problemsets, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_problems(request):
    user_id = utils.get_user_id_by_request(request)
    me = account_service.get_user_by_id(user_id)
    problemsets = problemset_service.get_my_published_problemset(me)
    serializer = ProblemsetSerializer(problemsets, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsProblemsetOwner])
def toggle(request, slug):
    problemset_service.toggle(slug)
    return JsonResponse(
        data={
            'message': "Successfully Ends Contest"
        },
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_contest_problems(request, slug):
    oj_problems_for_contest = problemset_service.get_all_oj_problems_from_problemset(
        slug)
    serializer = OJProblemForContestSerializer(
        oj_problems_for_contest, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_contest_problems_slug(request, slug):
    oj_problems_for_contest = problemset_service.get_all_oj_problems_from_problemset(
        slug)
    serializer = BodylessOJProblemForContestSerializer(
        oj_problems_for_contest, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminRole])
def get_submissions_in_problemset(request, slug):
    problemset = problemset_service.get_problemset_by_slug(slug)
    submissions = problemset_service.get_submissions(slug, problemset.type)
    serializer = OJSubmissionSerializer(submissions, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_submissions(request, slug):
    my_user_id = utils.get_user_id_by_request(request)
    problemset = problemset_service.get_problemset_by_slug(slug)
    submissions = problemset_service.get_my_submissions(
        slug, my_user_id, problemset.type)
    serializer = OJSubmissionSerializer(submissions, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_problemset_slugs(request):
    slugs = problemset_service.get_problemset_slugs()
    return JsonResponse(
        data=slugs,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_oj_problem(request, oj_name, oj_problem_code):
    try:
        problem = problemset_service.get_oj_problem(oj_name, oj_problem_code)
        serializer = OJProblemSerializer(problem, many=False)
        return JsonResponse(
            data=serializer.data,
            safe=False,
            status=200
        )
    except Exception as e:
        print(e)
        return JsonResponse(
            data={
                'message': 'Resource does not exist or failed to fetch',
            },
            safe=False,
            status=500
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsEligibleWorkingOnProblemset])
def submit_oj_problem(request):
    oj_name = request.data.get('oj_name')
    oj_problem_code = request.data.get('oj_problem_code')
    source_code = request.data.get('source_code')
    slug = request.data.get('slug')

    if slug is not None:
        problemset = problemset_service.get_problemset_by_slug(slug)

    user_id = utils.get_user_id_by_request(request)
    crawl_request = problemset_service.submit_oj_problem(
        oj_name, oj_problem_code, source_code, user_id, problemset)
    serializer = CrawlRequestSerializer(crawl_request, many=False)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_submission_id_from_crawl_request(request, crawl_request_id):
    crawl_request = webdriver_service.get_crawl_request_by_id(crawl_request_id)

    serializer = CrawlRequestSerializer(crawl_request, many=False)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_oj_submission_verdict(request, oj_name, oj_problem_code, submission_id):
    user_id = utils.get_user_id_by_request(request)
    verdict = problemset_service.get_oj_submission_verdict(
        oj_name, submission_id, user_id, oj_problem_code)
    return JsonResponse(
        data=verdict,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_oj_submission_verdict_for_contest(request, oj_name, oj_problem_code, submission_id, slug):
    oj_submission = problemset_service.get_oj_submission_verdict(
        oj_name, submission_id, oj_problem_code)
    serializer = OJSubmissionSerializer(oj_submission, many=False)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_oj_submissions_history(request, oj_name, oj_problem_code):
    user_id = utils.get_user_id_by_request(request)
    submissions = problemset_service.get_oj_submissions_history(
        oj_name, oj_problem_code, [user_id])
    serializer = OJSubmissionSerializer(submissions, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_oj_submissions_history_for_contest(request, oj_name, oj_problem_code, slug):
    user_id = utils.get_user_id_by_request(request)
    problemset = problemset_service.get_problemset_by_slug(slug)
    submissions = problemset_service.get_oj_submissions_history(
        oj_name, oj_problem_code, [user_id], problemset)
    serializer = OJSubmissionSerializer(submissions, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_oj_submissions_history_for_contest(request, oj_name, oj_problem_code, slug):
    problemset = problemset_service.get_problemset_by_slug(slug)
    submissions = problemset_service.get_all_oj_submissions_history(
        oj_name, oj_problem_code, problemset)
    serializer = OJSubmissionSerializer(submissions, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_users_oj_submissions_history_for_contest(request, oj_name, oj_problem_code, slug, email):
    problemset = problemset_service.get_problemset_by_slug(slug)
    user_ids = []
    if not email.isnumeric():
        user_id = account_service.get_user_by_email(email).id
        user_ids = [user_id]
    else:
        user_ids = problemset_service.get_team_members_from_team_id(email)

    submissions = problemset_service.get_oj_submissions_history(
        oj_name, oj_problem_code, user_ids, problemset)
    serializer = OJSubmissionSerializer(submissions, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOJSubmissionOwner])
def get_oj_submission_detail(request, id):
    submission = problemset_service.get_oj_submission_detail(id)
    serializer = OJSubmissionDetailSerializer(submission, many=False)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_contest_leaderboard(request, slug):
    user_id = utils.get_user_id_by_request(request)
    only_show_mine = (request.query_params.get('only_show_mine', 'false'))
    submissions = problemset_service.get_contest_leaderboard(
        slug, user_id, only_show_mine == 'true')
    return JsonResponse(
        data=submissions,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_problemset_meta(request, slug):
    problemset = problemset_service.get_problemset_by_slug(slug)
    serializer = ProblemsetSerializer(problemset, many=False)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_new_problemset(request):
    problemset_dict = request.data
    user_id = utils.get_user_id_by_request(request)
    user = account_service.get_user_by_id(user_id)
    problemset = problemset_service.create_new_problemset(
        problemset_dict, user)
    serializer = ProblemsetSerializer(problemset, many=False)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["POST"])
@permission_classes([IsProblemsetOwner])
def update_contest_problem(request, slug):
    problems_dict = request.data
    user_id = utils.get_user_id_by_request(request)
    user = account_service.get_user_by_id(user_id)
    problemset = problemset_service.update_problemset(
        problems_dict, user, slug)
    return JsonResponse(
        data={
            'message': 'Successfully update problems'
        },
        safe=False,
        status=200
    )


@api_view(["POST"])
@permission_classes([IsProblemsetOwner])
def delete_oj_problem_for_contest(request, slug):
    oj_name = request.data.get('oj_name')
    oj_problem_code = request.data.get('oj_problem_code')
    problemset_service.remove_oj_problem_for_contest(
        slug, oj_name, oj_problem_code)
    return JsonResponse(
        data={
            'message': 'Successfully delete problems'
        },
        safe=False,
        status=200
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_contest(request, slug):
    user_id = utils.get_user_id_by_request(request)
    user = account_service.get_user_by_id(user_id)
    problemset_service.register_contest(user, slug)
    return JsonResponse(
        data={
            'message': 'Successfully registered'
        },
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAdminRole])
def get_participants_for_contest(request, slug):
    problemset_eligibility = problemset_service.get_participants_for_contest(
        slug)
    serializer = ProblemsetEligibilitySerializer(
        problemset_eligibility, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["POST"])
@permission_classes([IsAdminRole])
def update_participant_status_for_contest(request):
    problemset_eligibility_id = request.data.get('id')
    value = request.data.get('value')
    user_id = utils.get_user_id_by_request(request)
    admin = account_service.get_user_by_id(user_id)
    problemset_eligibility = problemset_service.update_participant_status(
        problemset_eligibility_id, value, admin)

    serializer = ProblemsetEligibilitySerializer(
        problemset_eligibility, many=False)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_teams(request):
    user = account_service.get_user_by_request(request)
    team = problemset_service.get_my_teams(user)
    serializer = TeamSerializer(team, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_team_in_problemset(request, slug):
    user = account_service.get_user_by_request(request)
    team = problemset_service.get_user_team_in_problemset(user, slug)
    if team is None:
        return JsonResponse(
            data={
                'message': 'You have not registered in a team for this contest'
            },
            safe=False,
            status=403
        )

    serializer = TeamForProblemsetSerializer(team, many=False)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_team_members(request):
    team_name = request.data.get('team').get('name')
    emails = request.data.get('team').get('members')
    MAX_ALLOWED_TEAM_MEMBERS = 3
    if len(emails) > MAX_ALLOWED_TEAM_MEMBERS:
        return JsonResponse(
            data={
                'message': f'Team members should have at most {MAX_ALLOWED_TEAM_MEMBERS} members',
            },
            safe=False,
            status=400
        )

    team = problemset_service.register_team_members(team_name, emails)
    serializer = TeamSerializer(team, many=False)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_team_for_contest(request, slug):
    team_id = request.data.get('team_id')
    problemset_service.register_team_for_contest(team_id, slug)
    return JsonResponse(
        data={
            'message': 'Successfully registered team'
        },
        safe=False,
        status=200
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_team_members_by_id(request, team_id):
    members = problemset_service.get_team_members_from_team_id(team_id)
    serializer = UserSerializer(members, many=True)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )
