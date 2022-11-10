from rest_framework import serializers

from .models import (
    OJSubmission,
    Problemset,
    ProblemsetEligibility,
    OJProblem,
    OJProblemForContest,
    Team,
    TeamForProblemset
)
from root.modules.accounts.serializers import UserSerializer, UserOnlyNameSerializer


class ProblemsetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problemset
        fields = '__all__'


class ProblemsetTitleAndSlugOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Problemset
        fields = ['title', 'slug']


class OJProblemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OJProblem
        fields = '__all__'


class OJSubmissionSerializer(serializers.ModelSerializer):
    user = UserOnlyNameSerializer(many=False, read_only=True)

    class Meta:
        model = OJSubmission
        fields = ['verdict', 'status', 'submitted_at',
                  'id', 'oj_name', 'oj_problem_code', 'user', 'submission_id']


class OJSubmissionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OJSubmission
        fields = ['verdict', 'submitted_at',
                  'source_code']


class OJProblemForContestSerializer(serializers.ModelSerializer):
    oj_problem = OJProblemSerializer(many=False, read_only=True)
    problemset = ProblemsetSerializer(many=False, read_only=True)

    class Meta:
        model = OJProblemForContest
        fields = '__all__'


class BodylessOJProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OJProblem
        fields = ['id', 'oj_name', 'oj_problem_code']


class BodylessOJProblemForContestSerializer(serializers.ModelSerializer):
    oj_problem = BodylessOJProblemSerializer(many=False, read_only=True)
    problemset = ProblemsetSerializer(many=False, read_only=True)

    class Meta:
        model = OJProblemForContest
        fields = '__all__'


class ProblemsetEligibilitySerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    problemset = ProblemsetSerializer(many=False)

    class Meta:
        model = ProblemsetEligibility
        exclude = ['admitted_by']


class TeamSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True)

    class Meta:
        model = Team
        fields = '__all__'


class TeamForProblemsetSerializer(serializers.ModelSerializer):
    team = TeamSerializer(many=False)

    class Meta:
        model = TeamForProblemset
        fields = '__all__'