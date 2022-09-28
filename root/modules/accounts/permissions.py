from rest_framework.permissions import BasePermission
import root.modules.accounts.utils as utils
from .models import UserAccount


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user_id = utils.get_user_id_by_request(request)
        user = UserAccount.objects.get(id=user_id)
        return user.role == 'Admin'
