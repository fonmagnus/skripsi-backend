from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'name', 'role')


class UserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'name',
            'role',
            'profile_photo',
        )


class UserOnlyNameSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('name', )


class UserOnlyNameAndUsernameSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('name', 'username')


class UserOnlyNameAndEmailSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('name', 'email')
