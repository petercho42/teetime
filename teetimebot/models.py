import time
from datetime import date, datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

import teetimebot.datetime_helper as datetime_helper
from teetimebot.twilio_client import TwilioClient
from teetimebot.email_client import EmailClient


class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone_number = PhoneNumberField()


class UserNotifications(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    text = models.BooleanField(default=False)
    email = models.BooleanField(default=True)


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

    booking_vendor = models.CharField(max_length=20, choices=BookingVendor.choices)


class CourseSchedule(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    schedule_id = models.IntegerField()
    booking_class = models.IntegerField(null=True, blank=True)

    @property
    def schedule_url(self):
        if self.course.booking_vendor == Course.BookingVendor.TEEOFF:
            return f'https://www.teeoff.com/tee-times/facility/{str(self.schedule_id)}-{self.course.name.replace(" ", "-")}/search'
        elif self.course.booking_vendor == Course.BookingVendor.FOREUP:
            return f"https://foreupsoftware.com/index.php/booking/{str(self.course.id)}/{str(self.schedule_id)}#/teetimes"


class UserTeeTimeRequest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    date = models.DateField(default=None, null=True, blank=True)

    class DaysChoices(models.TextChoices):
        EVERY_DAY = "every day", _("Every day")
        EVERY_FRIDAY = "every friday", _("Every Friday")
        WEEKDAYS = "weekdays", _("Weekdays")
        WEEKENDS = "weekends", _("Weekends")
        TODAY = "today", _("Today")

    days = models.CharField(
        max_length=20,
        choices=DaysChoices.choices,
        default=None,
        null=True,
        blank=True,
    )
    tee_time_min = models.TimeField(default=None, null=True, blank=True)
    tee_time_max = models.TimeField(default=None, null=True, blank=True)
    search_time_min = models.TimeField(default=None, null=True, blank=True)
    search_time_max = models.TimeField(default=None, null=True, blank=True)

    class SearchDayChoices(models.TextChoices):
        EVERY_DAY = "every day", _("Every day")
        WEEKDAYS = "weekdays", _("Weekdays")
        WEEKENDS = "weekends", _("Weekends")

    search_day = models.CharField(
        max_length=20,
        choices=SearchDayChoices.choices,
        default=SearchDayChoices.EVERY_DAY,
        null=True,
        blank=True,
    )

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

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(search_time_min__isnull=True, search_time_max__isnull=True)
                | Q(search_time_min__isnull=False, search_time_max__isnull=False),
                name="both_fields_null_or_filled",
            )
        ]

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
                self.save(update_fields=["status"])
                print(f"Request ID {self.id} expired")
            elif date.today() == self.date:
                # Expire search 3hrs before the teetime
                if self.tee_time_max is not None:
                    if self.course.booking_vendor == Course.BookingVendor.FOREUP:
                        hours_delta = 3
                    if self.course.booking_vendor == Course.BookingVendor.TEEOFF:
                        hours_delta = 1
                    expiration_time = (
                        datetime.combine(date.today(), self.tee_time_max)
                        - timedelta(hours=hours_delta)
                    ).time()
                    if datetime.now().time() >= expiration_time:
                        self.status = UserTeeTimeRequest.Status.EXPIRED
                        self.save(update_fields=["status"])
                        print(f"Request ID {self.id} expired")

    def search_time(self, target_date):
        time_now = datetime.now().time()

        if self.search_day == UserTeeTimeRequest.SearchDayChoices.WEEKDAYS:
            if date.today().weekday() > 4:
                print(f"Won't search: today is not a weekday")
                return False
        elif self.search_day == UserTeeTimeRequest.SearchDayChoices.WEEKENDS:
            if date.today().weekday() < 5:
                print(f"Won't search: today is not a weekend")
                return False

        if self.search_time_min and self.search_time_max:
            if (time_now < self.search_time_min) or (time_now > self.search_time_max):
                print(f"Time is not {self.search_time_min} yet")
                return False
        if self.tee_time_max and target_date == date.today():
            # Stop searching x hour before tee_time_max
            if self.course.booking_vendor == Course.BookingVendor.FOREUP:
                hours_delta = 3
            elif self.course.booking_vendor == Course.BookingVendor.TEEOFF:
                hours_delta = 1
            expiration_time = (
                datetime.combine(date.today(), self.tee_time_max)
                - timedelta(hours=hours_delta)
            ).time()
            if time_now >= expiration_time:
                print(f"{date.today()} Won't search: tee_time_max too close")
                return False
        return True

    def hibernate(self):
        if self.search_time_min and self.search_time_max:
            time_now = datetime.now().time()
            if time_now < self.search_time_min:
                # Calculate the time difference
                time_until_min = datetime.combine(
                    datetime.today(), self.search_time_min
                ) - datetime.combine(datetime.today(), time_now)
            elif time_now > self.search_time_max:
                # Hibernate until the next day self.search_time_min
                time_until_min = datetime.combine(
                    datetime.today() + timedelta(days=1), self.search_time_min
                ) - datetime.combine(datetime.today(), time_now)

            total_seconds = time_until_min.total_seconds()

            # Calculate days, hours, minutes, and seconds
            days = int(total_seconds // (60 * 60 * 24))
            hours = int((total_seconds % (60 * 60 * 24)) // (60 * 60))
            minutes = int((total_seconds % (60 * 60)) // 60)
            seconds = int(total_seconds % 60)

            time_until_min_str = f"{seconds} seconds"
            if minutes:
                time_until_min_str = f"{minutes} minutes, {time_until_min_str}"
            if hours:
                time_until_min_str = f"{hours} hours, {time_until_min_str}"
            if days:
                time_until_min_str = f"{days} days, {time_until_min_str}"

            print(f"Hibernating for {time_until_min_str}")
            time.sleep(total_seconds)

    @property
    def target_dates(self):
        if self.date:
            return [self.date]
        else:
            if self.days == UserTeeTimeRequest.DaysChoices.TODAY:
                return [date.today()]
            elif self.days == UserTeeTimeRequest.DaysChoices.EVERY_DAY:
                return datetime_helper.get_next_dates("every_day")
            elif self.days == UserTeeTimeRequest.DaysChoices.WEEKDAYS:
                return datetime_helper.get_next_dates("weekdays")
            elif self.days == UserTeeTimeRequest.DaysChoices.WEEKENDS:
                return datetime_helper.get_next_dates("weekends")
            elif self.days == UserTeeTimeRequest.DaysChoices.EVERY_FRIDAY:
                return datetime_helper.get_next_dates("every_friday")
            else:
                raise Exception("TeeTime request is missing target dates!")


class MatchingTeeTime(models.Model):
    """
    Stores instances of tee-times found per user requests (UserTeeTimeRequest)
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_request = models.ForeignKey(UserTeeTimeRequest, on_delete=models.PROTECT)
    course_schedule = models.ForeignKey(CourseSchedule, on_delete=models.PROTECT)

    class Status(models.TextChoices):
        AVAILABLE = (
            "available",
            _("Available"),
        )
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
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_request", "course_schedule", "date", "time"],
                name="unique_matching_teetime",
            )
        ]

    @staticmethod
    def update_or_create_instance(user_request, schedule, tee_time_dict):
        if user_request.course.booking_vendor == Course.BookingVendor.FOREUP:
            tee_time_datetime = datetime.strptime(
                tee_time_dict["time"], "%Y-%m-%d %H:%M"
            )
            tee_time_date = tee_time_datetime.date()
            tee_time_time = tee_time_datetime.time()
            available_spots = tee_time_dict["available_spots"]
            price = tee_time_dict["green_fee"]
        elif user_request.course.booking_vendor == Course.BookingVendor.TEEOFF:
            tee_time_datetime = datetime.strptime(
                tee_time_dict["teeTime"], "%Y-%m-%dT%H:%M:%S"
            )
            tee_time_date = tee_time_datetime.date()
            tee_time_time = tee_time_datetime.time()
            available_spots = tee_time_dict["rounds"]
            price = tee_time_dict["formattedPrice"].replace("$", "")

        lookup_params = {
            "user_request": user_request,
            "course_schedule": schedule,
            "date": tee_time_date,
            "time": tee_time_time,
        }
        defaults = {
            "available_spots": available_spots,
            "price": price,
            "status": MatchingTeeTime.Status.AVAILABLE,
        }

        # Attempt to update the available-spot and price of an existing match or create a new match
        match, created = MatchingTeeTime.objects.update_or_create(
            defaults=defaults, **lookup_params
        )

    @staticmethod
    def process_gone_matching_tee_times(
        user_request, schedule, date, available_tee_times
    ):
        if user_request.course.booking_vendor == Course.BookingVendor.FOREUP:
            available_tee_time_objs = [
                datetime.strptime(tt, "%Y-%m-%d %H:%M").time()
                for tt in available_tee_times
            ]
        elif user_request.course.booking_vendor == Course.BookingVendor.TEEOFF:
            available_tee_time_objs = [
                datetime.strptime(tt, "%Y-%m-%dT%H:%M:%S").time()
                for tt in available_tee_times
            ]
        gone_matches = MatchingTeeTime.objects.filter(
            user_request=user_request,
            course_schedule=schedule,
            date=date,
            status=MatchingTeeTime.Status.AVAILABLE,
        ).exclude(time__in=available_tee_time_objs)
        for match in gone_matches:
            # save each object individually instead of .update(..) to trigger post_save receiver for notifications
            match.status = MatchingTeeTime.Status.GONE
            match.save(update_fields=["status"])


@receiver(post_save, sender=MatchingTeeTime)
def create_match_notification(sender, instance, created, **kwargs):
    reemerged = False
    price_change = False
    spots_change = False
    match_history = MatchingTeeTime.history.filter(id=instance.id).order_by(
        "-history_id"
    )
    if len(match_history) >= 2:
        if (
            match_history[0].status == MatchingTeeTime.Status.AVAILABLE
            and match_history[1].status == MatchingTeeTime.Status.GONE
        ):
            reemerged = True
        if match_history[0].price != match_history[1].price:
            price_change = True
            old_price = match_history[1].price
        if match_history[0].available_spots != match_history[1].available_spots:
            spots_change = True
            old_spots = match_history[1].available_spots

    if (
        created
        or reemerged
        or price_change
        or spots_change
        or instance.status == MatchingTeeTime.Status.GONE
        or instance.user_request.course.booking_vendor == Course.BookingVendor.FOREUP
    ):
        if instance.status == MatchingTeeTime.Status.AVAILABLE:
            subject = f'{instance.date.strftime("%A %m/%d/%y")}: {instance.course_schedule.name} @{instance.time.strftime("%I:%M %p")} for {instance.available_spots} ${instance.price}.'
            body = f'{subject}\nFound at {instance.updated_at.strftime("%I:%M:%S %p")}\n{instance.course_schedule.schedule_url}'
            if reemerged:
                subject = f"[Reemerged]{subject}"
            if price_change:
                subject = f"[Price Change]{subject}"
                body = f"Price change: ${old_price} -> ${instance.price}\n{body}"
            if spots_change:
                subject = f"[Available Spots Change]{subject}"
                body = f"Available spots change: {old_spots} -> {instance.available_spots}\n{body}"
        elif instance.status == MatchingTeeTime.Status.GONE:
            subject = f'[Gone]{instance.date.strftime("%A %m/%d/%y")}: {instance.course_schedule.name} @{instance.time.strftime("%I:%M %p")} ${instance.price}.'
            body = f'{subject}\nFound at {instance.created_at.strftime("%I:%M:%S %p")}\nGone at {instance.updated_at.strftime("%I:%M:%S %p")}'
        print(subject)
        if instance.user_request.user.notifications.text:
            MatchingTeeTimeNotification.objects.create(
                matching_tee_time=instance,
                type=MatchingTeeTimeNotification.Type.TEXT,
                to_phone_number=instance.user_request.user.phone_number,
                body=subject,  # only send subject as the whole content for texts
            )
        if instance.user_request.user.notifications.email:
            MatchingTeeTimeNotification.objects.create(
                matching_tee_time=instance,
                type=MatchingTeeTimeNotification.Type.EMAIL,
                to_email=instance.user_request.user.email,
                subject=subject,
                body=body,
            )


post_save.connect(create_match_notification, sender=MatchingTeeTime)


class MatchingTeeTimeNotification(models.Model):
    """
    Snapshot of notification sent to user
    """

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
    to_phone_number = PhoneNumberField(default=None, null=True, blank=True)
    subject = models.TextField(default=None, null=True, blank=True)
    body = models.TextField()
    sent = models.BooleanField(default=False)
    error_type = models.TextField()
    error_message = models.TextField()


@receiver(post_save, sender=MatchingTeeTimeNotification)
def send_match_notification(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.type == MatchingTeeTimeNotification.Type.TEXT:
                TwilioClient.send_message(str(instance.to_phone_number), instance.body)
            elif instance.type == MatchingTeeTimeNotification.Type.EMAIL:
                EmailClient.send_email_with_outlook(
                    instance.to_email, instance.subject, instance.body
                )
            instance.sent = True
            instance.save(update_fields=["sent"])
        except Exception as e:
            print(f"Error send_match_notification {e}")


post_save.connect(send_match_notification, sender=MatchingTeeTimeNotification)


class ForeUpUser(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)  # encrypt this in v1.0
    course_id = models.IntegerField()  # e.g. 19765 for Bethpage
    booking_class = models.IntegerField()
