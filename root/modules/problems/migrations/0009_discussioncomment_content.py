# Generated by Django 3.1 on 2022-12-11 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0008_auto_20221211_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='discussioncomment',
            name='content',
            field=models.TextField(default=None),
        ),
    ]
