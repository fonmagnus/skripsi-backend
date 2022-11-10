# Generated by Django 3.1 on 2022-09-01 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OJLoginAccountInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_or_username', models.CharField(max_length=256)),
                ('password', models.CharField(max_length=256)),
                ('oj_name', models.CharField(max_length=256)),
                ('last_login', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CrawlRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oj_name', models.CharField(blank=True, max_length=255, null=True)),
                ('submission_id', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(default='Pending', max_length=255)),
                ('oj_login_account_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webdriver.ojloginaccountinfo')),
            ],
        ),
    ]