from root.modules.accounts.models import UserAccount
from cloudinary import uploader


class AccountDbAccessor:
    def get_user_by_id(self, id):
        return UserAccount.objects.get(id=id)

    def get_user_by_email(self, email):
        return UserAccount.objects.get(email=email)

    def upload_profile_photo(self, user_id, photo):
        response = uploader.upload(photo)
        user = UserAccount.objects.get(id=user_id)
        user.profile_photo = response.get('public_id')
        user.save()
