# Generated by Django 3.1 on 2022-11-10 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0005_ojsubmission_subtask_results'),
    ]

    operations = [
        migrations.AddField(
            model_name='ojproblem',
            name='type',
            field=models.CharField(choices=[('batch', 'Batch'), ('interactive', 'Interactive'), ('output_only', 'Output Only')], default='batch', max_length=255),
        ),
    ]
