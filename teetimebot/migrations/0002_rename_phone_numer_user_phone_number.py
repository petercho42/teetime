# Generated by Django 4.2.1 on 2023-07-20 15:11

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("teetimebot", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="phone_numer",
            new_name="phone_number",
        ),
    ]
