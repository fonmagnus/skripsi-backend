# ./bookstore_app/api/urls.py

from django.urls import include, path
from root.api.v1 import accounts

urlpatterns = [
    path('me', accounts.me),
    path('logout', accounts.logout),
    path('upload-profile-photo', accounts.upload_profile_photo),
    path('activate/<str:uidb64>/<str:token>', accounts.activate),
]
