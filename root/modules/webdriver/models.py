from django.db import models

# Create your models here.


class OJLoginAccountInfo(models.Model):
    email_or_username = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
    oj_name = models.CharField(max_length=256)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email_or_username


class CrawlRequest(models.Model):
    oj_name = models.CharField(max_length=255, blank=True, null=True)
    submission_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, default='Pending')
    oj_login_account_info = models.ForeignKey(
        OJLoginAccountInfo, on_delete=models.CASCADE, blank=True, null=True)
