from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from root.modules.accounts.models import UserAccount
import jwt


# we don't need to decode the same token multiple times
jwt_decode_cache = {}


def get_user_id_by_request(request):
    access_token = request.headers.get('Authorization').split(" ")[1]
    if not access_token in jwt_decode_cache.keys():
        jwt_decode_cache[access_token] = jwt.decode(
            access_token, verify=False).get("user_id")
    return jwt_decode_cache[access_token]


def get_user_by_request(request):
    user_id = get_user_id_by_request(request)
    user = UserAccount.objects.get(id=user_id)
    return user


User = get_user_model()


class AuthBackend(ModelBackend):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, username=None, password=None):
        print('inside custom auth')
        try:
            user = User.objects.get(
                Q(username=username) | Q(email=username))
            print(user)
        except User.DoesNotExist:
            return None
        print(user)
        if user.check_password(password):
            return user
        else:
            return None
