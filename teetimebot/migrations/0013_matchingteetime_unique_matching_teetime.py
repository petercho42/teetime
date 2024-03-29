# Generated by Django 4.2.1 on 2023-08-06 21:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("teetimebot", "0012_alter_matchingteetimenotification_sent_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="matchingteetime",
            constraint=models.UniqueConstraint(
                fields=("user_request", "course_schedule", "date", "time"),
                name="unique_matching_teetime",
            ),
        ),
    ]
