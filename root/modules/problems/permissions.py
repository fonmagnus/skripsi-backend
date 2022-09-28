from rest_framework.permissions import BasePermission
import root.modules.accounts.utils as utils
from root.modules.accounts.models import UserAccount

from root.modules.problems.models import ProblemsetEligibility, Problemset, OJSubmission
from django.utils import timezone


class IsEligibleWorkingOnProblemset(BasePermission):
    def has_permission(self, request, view):
        user_id = utils.get_user_id_by_request(request)
        problemset_slug = view.kwargs.get(
            'slug') if request.method == 'GET' else request.data.get('slug')
        user = UserAccount.objects.get(id=user_id)

        if user.role == 'Admin':
            return True

        problemset = Problemset.objects.get(slug=problemset_slug)

        if timezone.now() < problemset.start_at:
            return False

        is_eligible = ProblemsetEligibility.objects.filter(
            user__id=user_id,
            problemset__slug=problemset_slug,
            is_eligible=True,
        ).exists()
        return is_eligible


class IsProblemsetOwner(BasePermission):
    def has_permission(self, request, view):
        user_id = utils.get_user_id_by_request(request)
        user = UserAccount.objects.get(id=user_id)

        if user.role == 'Admin':
            return True

        slug = view.kwargs.get('slug')
        return Problemset.objects.filter(slug=slug, created_by__id=user_id).exists()


class IsLeaderboardEnabled(BasePermission):
    def has_permission(self, request, view):
        problemset_slug = view.kwargs.get('slug')
        problemset = Problemset.objects.get(slug=problemset_slug)
        return problemset.is_leaderboard_enabled


class IsOJSubmissionOwner(BasePermission):
    def has_permission(self, request, view):
        user_id = utils.get_user_id_by_request(request)
        id = view.kwargs.get('id')
        user = UserAccount.objects.get(id=user_id)
        oj_submission = OJSubmission.objects.filter(id=id, user=user)

        if user.has_perm('get', 'submissions'):
            return True

        if user.role == 'Admin':
            return True

        return oj_submission.exists()
