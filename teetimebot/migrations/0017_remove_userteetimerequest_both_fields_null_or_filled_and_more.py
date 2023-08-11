# Generated by Django 4.2.1 on 2023-08-10 14:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("teetimebot", "0016_remove_userteetimerequest_recurring_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="userteetimerequest",
            name="both_fields_null_or_filled",
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