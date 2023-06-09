from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import AbstractUser

from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone_numer = PhoneNumberField()

# Create your models here.

class Course(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200)

    class BookingVendor(models.TextChoices):
        FOREUP = "ForeUP", _("ForeUp")
    booking_vendor = models.CharField(
        max_length=20,
        choices=BookingVendor.choices,
    )
    

class UserTeeTimeRequest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    date = models.DateField()
    tee_time_min = models.TimeField(default=None, null=True, blank=True)
    tee_time_max = models.TimeField(default=None, null=True, blank=True)
    class Players(models.IntegerChoices):
        ANY = 0
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
    players = models.IntegerField(choices=Players.choices, default=Players.ANY)
    class Holes(models.IntegerChoices):
        NINE = 9
        EIGHTEEN = 18
    holes = models.IntegerField(choices=Holes.choices, default=Holes.EIGHTEEN)



class ForeUpUser():
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)  # encrypt this in v1.0
    course_id = models.IntegerField()  # e.g. 19765 for Bethpage
    booking_class = models.IntegerField()

    

class ForeUpCourseInformation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    schedule_id = models.IntegerField()


 