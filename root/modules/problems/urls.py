# ./bookstore_app/api/urls.py

from django.urls import include, path
from root.api.v1 import problemset

urlpatterns = [
    path('all/my', problemset.get_my_problems),
    path('all', problemset.get_all_problems),
    path('toggle/<slug:slug>', problemset.toggle),
    path('get-submissions/<slug:slug>', problemset.get_submissions_in_problemset),
    path('get-my-submissions/<slug:slug>', problemset.get_my_submissions),
    path('get-oj-problem/<str:oj_name>/<str:oj_problem_code>',
         problemset.get_oj_problem),
    path('submit-oj-problem', problemset.submit_oj_problem),

    path('get-crawl-request/<int:crawl_request_id>',
         problemset.get_submission_id_from_crawl_request),
    path('get-oj-submission-verdict/<str:oj_name>/<str:oj_problem_code>/<str:submission_id>',
         problemset.get_oj_submission_verdict),
    path('get-oj-submission-verdict-for-contest/<str:oj_name>/<str:oj_problem_code>/<str:submission_id>/<slug:slug>',
         problemset.get_oj_submission_verdict_for_contest),
    path('get-oj-submissions-history/<str:oj_name>/<str:oj_problem_code>',
         problemset.get_oj_submissions_history),
    path('get-oj-submissions-history-for-contest/<str:oj_name>/<str:oj_problem_code>/<slug:slug>',
         problemset.get_oj_submissions_history_for_contest),
    path('get-all-oj-submissions-history-for-contest/<str:oj_name>/<str:oj_problem_code>/<slug:slug>',
         problemset.get_all_oj_submissions_history_for_contest),
    path('get-users-oj-submissions-history-for-contest/<str:oj_name>/<str:oj_problem_code>/<slug:slug>/<str:email>',
         problemset.get_users_oj_submissions_history_for_contest),


    path('get-oj-submission-detail/<int:id>',
         problemset.get_oj_submission_detail),

    path('get-contest-problems/<slug:slug>',
         problemset.get_contest_problems),
    path('get-contest-problems-slug/<slug:slug>',
         problemset.get_contest_problems_slug),
    path('get-contest-leaderboard/<slug:slug>',
         problemset.get_contest_leaderboard),

    path('get-problemset-meta/<slug:slug>',
         problemset.get_problemset_meta),
    path('get-participants-for-contest/<slug:slug>',
         problemset.get_participants_for_contest),
    path('update-participant-status',
         problemset.update_participant_status_for_contest),
    path('problemset/new',
         problemset.create_new_problemset),
    path('problemset/update-contest-problem/<slug:slug>',
         problemset.update_contest_problem),

    path('get-my-team-in-problemset/<slug:slug>',
         problemset.get_my_team_in_problemset),
    path('get-my-teams',
         problemset.get_my_teams),
    path('get-team-members/<int:team_id>',
         problemset.get_team_members_by_id),
    path('register-team-members',
         problemset.register_team_members),
    path('register-team-for-contest/<slug:slug>',
         problemset.register_team_for_contest),


    path('problemset/delete-oj-problem-for-contest/<slug:slug>',
         problemset.delete_oj_problem_for_contest),
    path('register-contest/<slug:slug>',
         problemset.register_contest),
]
