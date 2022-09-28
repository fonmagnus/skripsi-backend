from django.contrib import admin
from .models import CrawlRequest, OJLoginAccountInfo
# Register your models here.


class OJLoginAccountInfoAdmin(admin.ModelAdmin):
    list_display = ['email_or_username', 'password', 'last_login', 'oj_name']

    class Meta:
        model = OJLoginAccountInfo

class CrawlRequestAdmin(admin.ModelAdmin):
    list_display = ['oj_name', 'submission_id', 'status', 'oj_login_account_info']

    class Meta:
        model = CrawlRequest

admin.site.register(OJLoginAccountInfo, OJLoginAccountInfoAdmin)
admin.site.register(CrawlRequest, CrawlRequestAdmin)
