from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'name', 'role']

    class Meta:
        model = User


admin.site.register(User, UserAccountAdmin)
