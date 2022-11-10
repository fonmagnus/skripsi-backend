from django.db import models
from root.modules.accounts.models import UserAccount
from tinymce.models import HTMLField
from root.modules.webdriver.models import OJLoginAccountInfo


class Problemset(models.Model):
    class Type(models.TextChoices):
        FULL_CODING = 'FULL_CODING'             # * OJ Problems

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    start_at = models.DateTimeField()
    duration_seconds = models.IntegerField()
    slug = models.SlugField(db_index=True)
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    show_greetings = models.BooleanField(default=False)
    greetings = HTMLField(null=True, blank=True)
    is_leaderboard_enabled = models.BooleanField(default=False)
    is_public_leaderboard_enabled = models.BooleanField(default=False)
    type = models.CharField(
        max_length=255, choices=Type.choices, default=Type.FULL_CODING)

    priority_index = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        UserAccount,
        db_index=True,
        on_delete=models.CASCADE,
        to_field='email',
        default='arnold.ardianto.aa@gmail.com'
    )
    enable_team_contest = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + ' ' + self.title


class ProblemsetEligibility(models.Model):
    problemset = models.ForeignKey(Problemset, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    is_eligible = models.BooleanField(default=True, db_index=True)


class ProblemTag(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    def __str__(self) -> str:
        return self.name


class OJProblem(models.Model):
    class ProblemType(models.TextChoices):
        batch = 'batch'
        interactive = 'interactive'
        output_only = 'output_only'
    oj_name = models.CharField(max_length=255, db_index=True)
    oj_problem_code = models.CharField(
        max_length=255, default=None, db_index=True)
    url = models.URLField()
    title = models.CharField(max_length=255, db_index=True)
    body = models.TextField(blank=True, null=True)
    time_limit = models.CharField(max_length=255, blank=True, null=True)
    memory_limit = models.CharField(max_length=255, blank=True, null=True)
    difficulty = models.FloatField(
        default=0, null=True, blank=True, db_index=True)
    tags = models.ManyToManyField(ProblemTag, blank=True, db_index=True)
    type = models.CharField(
        max_length=255, choices=ProblemType.choices, default=ProblemType.batch)

    def __str__(self):
        return self.oj_problem_code + " " + self.title + " " + self.oj_name


class OJSubmission(models.Model):
    class Status(models.TextChoices):
        Accepted = 'Accepted'
        Rejected = 'Rejected'
        Pending = 'Pending'

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    submission_id = models.CharField(
        max_length=255, db_index=True, blank=True, null=True)
    oj_name = models.CharField(max_length=255, db_index=True)
    oj_problem_code = models.CharField(
        max_length=255, default='', db_index=True)
    verdict = models.CharField(max_length=255, default='Pending')
    status = models.CharField(
        max_length=255, choices=Status.choices, blank=True, null=True)
    source_code = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    oj_login_account_info = models.ForeignKey(
        OJLoginAccountInfo, on_delete=models.CASCADE, null=True, blank=True)
    problemset = models.ForeignKey(
        Problemset, on_delete=models.CASCADE, blank=True, null=True, default=None)
    enable_partial_scoring = models.BooleanField(default=False)
    score = models.FloatField(default=0)
    subtask_results = models.TextField(null=True, blank=True)


class OJProblemForContest(models.Model):
    problemset = models.ForeignKey(Problemset, on_delete=models.CASCADE)
    oj_problem = models.ForeignKey(OJProblem, on_delete=models.CASCADE)
    priority_index = models.IntegerField(default=100)

    def __str__(self):
        return self.problemset.title + ' ' + self.oj_problem.title


class Team(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    members = models.ManyToManyField(UserAccount, db_index=True)

    def __str__(self):
        res = self.name + '-'
        for user in self.members.all():
            res += '-'
            res += user.name
        return res


class TeamForProblemset(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    problemset = models.ForeignKey(Problemset, on_delete=models.CASCADE)

    def __str__(self):
        return self.team.name + ' -- ' + self.problemset.title
