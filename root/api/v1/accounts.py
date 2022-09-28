from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.http import JsonResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from root.modules.accounts.models import UserAccount
from root.modules.accounts.serializers import UserSerializer
import root.modules.accounts.utils as utils

from root.services import account_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user_id = utils.get_user_id_by_request(request)
    user = UserAccount.objects.get(id=user_id)
    serializer = UserSerializer(user, many=False)
    return JsonResponse(
        data=serializer.data,
        safe=False,
        status=200
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    print(type(request.user))
    return JsonResponse(
        data={
            'message': 'Success Logout'
        },
        status=200
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def activate(request, uidb64=None, token=None):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserAccount.objects.get(pk=uid)
        print(user)
    except UserAccount.DoesNotExist:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.is_active = True
        user.save()
        print("Activaton done")
        return JsonResponse(
            data={
                'message': 'Success Activate Account'
            },
            status=200
        )
    else:
        print("Activation failed")
        return JsonResponse(
            data={
                'message': 'Unexpected server error when activate'
            },
            status=500
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_profile_photo(request):
    photo = request.data.get('photo')
    user_id = utils.get_user_id_by_request(request)
    account_service.upload_profile_photo(user_id, photo)
    return JsonResponse(
        data={
            'message': 'Successfully change photo'
        },
        status=200
    )
