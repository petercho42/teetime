# Generated by Django 4.2.1 on 2023-08-16 18:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("teetimebot", "0019_course_course_id_alter_userteetimerequest_days"),
    ]

    operations = [
        migrations.AddField(
            model_name="courseschedule",
            name="console_facility_id",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="courseschedule",
            name="facility_id",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="course",
            name="booking_vendor",
            field=models.CharField(
                choices=[
                    ("ForeUP", "ForeUp"),
                    ("TeeOff", "TeeOff"),
                    ("GOIBSVISION", "GOIBSVISION"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="courseschedule",
            name="schedule_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]