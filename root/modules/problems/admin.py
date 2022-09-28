from django.contrib import admin
from .models import (
    Problemset,
    ProblemsetEligibility,
    OJProblem,
    OJSubmission,
    OJProblemForContest,
    Team,
    TeamForProblemset
)

# Register your models here.


class ProblemsetAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_at', 'duration_seconds']

    class Meta:
        model = Problemset


class ProblemsetEligibilityAdmin(admin.ModelAdmin):
    list_display = ['problemset', 'user']

    class Meta:
        model = ProblemsetEligibility


class OJProblemAdmin(admin.ModelAdmin):
    list_display = ['oj_name', 'title', 'url']

    class Meta:
        model = OJProblem


class OJSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'submission_id', 'problemset',
                    'oj_name', 'oj_problem_code', 'verdict', 'submitted_at']

    class Meta:
        model = OJSubmission


class OJProblemForContestAdmin(admin.ModelAdmin):
    list_display = ['problemset', 'oj_problem']

    class Meta:
        model = OJProblemForContest


class TeamAdmin(admin.ModelAdmin):
    list_display = ['name']

    class Meta:
        model = Team


class TeamForProblemsetAdmin(admin.ModelAdmin):
    list_display = ['team', 'problemset']

    class Meta:
        model = TeamForProblemset


admin.site.register(Problemset, ProblemsetAdmin)
admin.site.register(ProblemsetEligibility, ProblemsetEligibilityAdmin)
admin.site.register(OJProblem, OJProblemAdmin)
admin.site.register(OJSubmission, OJSubmissionAdmin)
admin.site.register(OJProblemForContest, OJProblemForContestAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamForProblemset, TeamForProblemsetAdmin)
