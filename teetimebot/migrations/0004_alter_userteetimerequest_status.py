# Generated by Django 4.2.1 on 2023-07-26 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teetimebot', '0003_rename_booking_class_id_courseschedule_booking_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userteetimerequest',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('expired', 'Expired')], default='inactive', max_length=20),
        ),
    ]
