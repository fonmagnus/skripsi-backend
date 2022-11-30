from root.repositories.AccountDbAccessor import AccountDbAccessor
from root.modules.accounts import utils


class AccountService:
    def __init__(self, *args, **kwargs):
        self.db_accessor = AccountDbAccessor()

    def get_user_by_id(self, id):
        return self.db_accessor.get_user_by_id(id)

    def get_user_by_email(self, email):
        return self.db_accessor.get_user_by_email(email)

    def upload_profile_photo(self, user_id, photo):
        return self.db_accessor.upload_profile_photo(user_id, photo)

    def get_user_by_request(self, request):
        user_id = utils.get_user_id_by_request(request)
        return self.db_accessor.get_user_by_id(user_id)

    def get_user_by_username(self, id_or_username):
        return self.db_accessor.get_user_by_username(id_or_username)
