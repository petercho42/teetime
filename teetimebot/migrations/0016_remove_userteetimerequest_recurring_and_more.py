# Generated by Django 4.2.1 on 2023-08-10 14:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "teetimebot",
            "0015_rename_to_phone_numer_matchingteetimenotification_to_phone_number",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userteetimerequest",
            name="recurring",
        ),
        migrations.AddField(
            model_name="userteetimerequest",
            name="days",
            field=models.CharField(
                blank=True,
                choices=[
                    ("every day", "Every day"),
                    ("weekdays", "Weekdays"),
                    ("weekends", "Weekends"),
                    ("today", "Today"),
                ],
                default=None,
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="userteetimerequest",
            name="search_day",
            field=models.CharField(
                blank=True,
                choices=[
                    ("every day", "Every day"),
                    ("weekdays", "Weekdays"),
                    ("weekends", "Weekends"),
                ],
                default="every day",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="userteetimerequest",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("search_time_max__isnull", True),
                        ("search_time_min__isnull", True),
                    ),
                    models.Q(
                        ("search_time_max__isnull", False),
                        ("search_time_min__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="both_fields_null_or_filled",
            ),
        ),
    ]
