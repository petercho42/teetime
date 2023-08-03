from datetime import date, datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

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
        TEEOFF = "TeeOff", _("TeeOff")
    booking_vendor = models.CharField(
        max_length=20,
        choices=BookingVendor.choices
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
    date = models.DateField(default=None, null=True, blank=True)
    class RecurringPeriod(models.TextChoices):
        EVERY_DAY = "every day", _("Every day")
        WEEKDAYS = "weekdays", _("Weekdays")
        WEEKENDS = "weekends", _("Weekends")
    recurring = models.CharField(
        max_length=20,
        choices=RecurringPeriod.choices,
        default=None,
        null=True,
        blank=True
    )
    tee_time_min = models.TimeField(default=None, null=True, blank=True)
    tee_time_max = models.TimeField(default=None, null=True, blank=True)
    search_time_min = models.TimeField(default=None, null=True, blank=True)
    search_time_max = models.TimeField(default=None, null=True, blank=True)
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
        if self.date is not None:
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

class MatchingTeeTimeHistoricalRecords(HistoricalRecords):
    def should_create_historical_record(self, instance, **kwargs):
        # Check if the 'status', 'available_spots', or 'price' has changed
        if instance.pk is not None:
            previous_instance = instance.__class__.objects.get(pk=instance.pk)
            if instance.status != previous_instance.status:
                return True
            elif instance.available_spots != previous_instance.available_spots:
                return True
            elif instance.price != previous_instance.price:
                return True
        return False


class MatchingTeeTime(models.Model):
    '''
    Stores instances of tee-times found per user requests (UserTeeTimeRequest)
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_request = models.ForeignKey(UserTeeTimeRequest, on_delete=models.PROTECT)
    course_schedule = models.ForeignKey(CourseSchedule, on_delete=models.PROTECT)
    class Status(models.TextChoices):
        AVAILABLE = "available", _("Available"),
        GONE = "gone", _("Gone")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    date = models.DateField()
    time = models.TimeField()
    class Players(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
    available_spots = models.IntegerField(choices=Players.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Add the HistoricalRecords to track changes
    history = MatchingTeeTimeHistoricalRecords()


    @staticmethod
    def update_or_create_instance(user_request, schedule, tee_time_dict):
        if user_request.course.booking_vendor == Course.BookingVendor.FOREUP:
          tee_time_datetime = datetime.strptime(tee_time_dict['teeTime'], '%Y-%m-%dT%H:%M:%S')
          tee_time_date = tee_time_datetime.date()
          tee_time_time = tee_time_datetime.time()
          available_spots = tee_time_dict["rounds"]
          price = tee_time_dict["formattedPrice"]
        elif user_request.course.booking_vendor == Course.BookingVendor.TEEOFF:
            pass
            
        lookup_params = {
            'user_request': user_request,
            'course_schedule': schedule,
            'date': tee_time_date,
            'time': tee_time_time,
            }
        defaults = {
            'available_spots': available_spots,
            'price': price
        }

        # Attempt to update the available-spot and price of an existing match or create a new match
        book, created = MatchingTeeTime.objects.update_or_create(
            defaults=defaults,
            **lookup_params
        )


class MatchingTeeTimeNotification(models.Model):
    '''
    Snapshot of notification sent to user
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    matching_tee_time = models.ForeignKey(MatchingTeeTime, on_delete=models.PROTECT)
    class Type(models.TextChoices):
        TEXT = "text", _("Text")
        EMAIL = "email", _("Email")
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
    )
    to_email = models.EmailField(default=None, null=True, blank=True)
    to_phone_numer = PhoneNumberField(default=None, null=True, blank=True)
    subject = models.TextField(default=None, null=True, blank=True)
    body = models.TextField()
    sent = models.BooleanField()
    error_type = models.TextField()
    error_message = models.TextField()


class ForeUpUser(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)  # encrypt this in v1.0
    course_id = models.IntegerField()  # e.g. 19765 for Bethpage
    booking_class = models.IntegerField()

 