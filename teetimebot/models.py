from datetime import date, datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone_number = PhoneNumberField()

class UserNotifications(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    text = models.BooleanField(default=False)
    email = models.BooleanField(default=True)
    push = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def create_usernotifications(sender, instance, created, **kwargs):
    if created:
        UserNotifications.objects.get_or_create(user=instance)

post_save.connect(create_usernotifications, sender=User)   

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
        default=BookingVendor.FOREUP,
    )

class CourseSchedule(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    schedule_id = models.IntegerField()
    booking_class = models.IntegerField(null=True, blank=True)


class UserTeeTimeRequest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
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
    class Holes(models.TextChoices):
        ANY = "any", _("Any")
        NINE = "9", _("9")
        EIGHTEEN = "18", _("18")
    holes = models.CharField(
        max_length=20,
        choices=Holes.choices,
        default=Holes.ANY,
    )
    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")
        EXPIRED = "expired", _("Expired")
        PENDING = "pending", _("Pending")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INACTIVE,
    )
    def update_status_if_expired(self):
        if date.today() > self.date:
            self.status = UserTeeTimeRequest.Status.EXPIRED
            self.save(update_fields=['status'])
            print(f'Request ID {self.id} expired')
        elif date.today() == self.date:
            # stop searching 3hrs and 10 minutes before the teetime
            if self.course.id.booking_vendor == Course.BookingVendor.FOREUP:
                if self.tee_time_max is not None:
                    expiration_time = (self.tee_time_max - timedelta(hours=3, minutes=10)).time()
                    if datetime.now().time() >= expiration_time:
                        self.status = UserTeeTimeRequest.Status.EXPIRED
                        self.save(update_fields=['status'])



class ForeUpUser(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)  # encrypt this in v1.0
    course_id = models.IntegerField()  # e.g. 19765 for Bethpage
    booking_class = models.IntegerField()

 