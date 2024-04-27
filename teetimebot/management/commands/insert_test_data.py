from django.core.management.base import BaseCommand
from datetime import date, time
from teetimebot.models import (
    User,
    Course,
    CourseSchedule,
    UserTeeTimeRequest,
    ForeUpUser,
    MatchingTeeTime,
    MatchingTeeTimeNotification,
)

from phonenumber_field.phonenumber import PhoneNumber


class Command(BaseCommand):
    help = "Creates preminary data for testing purpose"

    """
    def add_arguments(self, parser):
        parser.add_argument("course_ids", nargs="+", type=int)
    """

    def handle(self, *args, **options):
        """
        Clean Data
        """
        MatchingTeeTimeNotification.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted All MatchingTeeTimeNotification Data")
        )
        MatchingTeeTime.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted All MatchingTeeTime Data"))
        MatchingTeeTime.history.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted All Historical MatchingTeeTime Data")
        )
        UserTeeTimeRequest.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted All UserTeeTimeRequest Data"))
        ForeUpUser.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted All ForeUpUser Data"))
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted All User Data"))
        CourseSchedule.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted All CourseSchedule Data"))
        Course.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted All Course Data"))

        """
        Create User
        """
        u = User.objects.create(
            first_name="Peter",
            last_name="Cho",
            email="monkeydluffy1p1p@gmail.com",
            phone_number=PhoneNumber.from_string("+19172820312"),
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created User {u.first_name} {u.last_name}, {u.phone_number}"
            )
        )

        """
        Create ForeUpUser
        """

        foreup_u = ForeUpUser.objects.create(
            user=u,
            username="monkeydluffy1p1p@gmail.com",
            password="",  # real password required
            course_id=19765,
            booking_class=2144,
        )
        self.stdout.write(self.style.SUCCESS(f"Created ForeUpUser {foreup_u.username}"))

        """
        Create Bethpage Course
        """
        bethpage = Course.objects.create(
            name="Bethpage State Park",
            booking_vendor=Course.BookingVendor.FOREUP,
            course_id=19765,
        )
        self.stdout.write(self.style.SUCCESS(f"Created Course {bethpage.name}"))

        """
        Create Bethpage Courses CourseSchedule
        """
        bethpage_black = CourseSchedule.objects.create(
            course=bethpage,
            name="Bethpage Black Course",
            schedule_id=2431,
            booking_class=2136,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created CourseSchedule {bethpage_black.name}")
        )

        bethpage_red = CourseSchedule.objects.create(
            course=bethpage,
            name="Bethpage Red Course",
            schedule_id=2432,
            booking_class=2138,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created CourseSchedule {bethpage_red.name}")
        )

        bethpage_blue = CourseSchedule.objects.create(
            course=bethpage,
            name="Bethpage Blue Course",
            schedule_id=2433,
            booking_class=2140,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created CourseSchedule {bethpage_blue.name}")
        )

        bethpage_green = CourseSchedule.objects.create(
            course=bethpage,
            name="Bethpage Green Course",
            schedule_id=2434,
            booking_class=2142,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created CourseSchedule {bethpage_green.name}")
        )

        bethpage_yellow = CourseSchedule.objects.create(
            course=bethpage,
            name="Bethpage Yellow Course",
            schedule_id=2435,
            booking_class=2144,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created CourseSchedule {bethpage_yellow.name}")
        )

        """
        Create Douglaston Course
        """
        douglaston = Course.objects.create(
            name="Douglaston Golf Course",
            booking_vendor=Course.BookingVendor.TEEOFF,
        )
        self.stdout.write(self.style.SUCCESS(f"Created Course {douglaston.name}"))

        douglaston_eighteen = CourseSchedule.objects.create(
            course=douglaston, name="Douglaston Golf Course 18 Hole", schedule_id=5044
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created CourseSchedule {douglaston_eighteen.name}")
        )

        """
        Create Kissena Course
        """
        kissena = Course.objects.create(
            name="Kissena Golf Course",
            booking_vendor=Course.BookingVendor.TEEOFF,
        )
        self.stdout.write(self.style.SUCCESS(f"Created Course {kissena.name}"))

        kissena_eighteen = CourseSchedule.objects.create(
            course=kissena, name="Kissena Golf Course 18 Hole", schedule_id=5046
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created CourseSchedule {kissena_eighteen.name}")
        )

        """
        Create Forest Park
        """
        forest_park = Course.objects.create(
            name="Forest Park Golf Course",
            booking_vendor=Course.BookingVendor.TEEOFF,
        )
        self.stdout.write(self.style.SUCCESS(f"Created Course {forest_park.name}"))

        forest_park_eighteen = CourseSchedule.objects.create(
            course=forest_park, name="Forest Park Golf Course 18 Hole", schedule_id=5045
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created CourseSchedule {forest_park_eighteen.name}")
        )

        """
        Create Willow Creek Golf & Country Club
        """
        willow_creek = Course.objects.create(
            name="Willow Creek Golf & Country Club",
            booking_vendor=Course.BookingVendor.TEEOFF,
        )
        self.stdout.write(self.style.SUCCESS(f"Created Course {willow_creek.name}"))

        willow_creek_eighteen = CourseSchedule.objects.create(
            course=willow_creek,
            name="Create Willow Creek Golf & Country Club 18 Hole",
            schedule_id=4749,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created CourseSchedule {willow_creek_eighteen.name}")
        )

        """
        Create West Point Golf Course
        """
        west_point = Course.objects.create(
            name="West Point Golf Course",
            booking_vendor=Course.BookingVendor.TEEOFF,
        )
        self.stdout.write(self.style.SUCCESS(f"Created Course {west_point.name}"))

        west_point_eighteen = CourseSchedule.objects.create(
            course=west_point,
            name="West Point Golf Course 18 Hole",
            schedule_id=6013,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created CourseSchedule {west_point_eighteen.name}")
        )

        """
        Create Harbor Links Course
        """
        harbor_links = Course.objects.create(
            name="Harbor Links Golf Course",
            booking_vendor=Course.BookingVendor.GOIBSVISION,
        )
        self.stdout.write(self.style.SUCCESS(f"Created Course {harbor_links.name}"))

        harbor_links_championship_course = CourseSchedule.objects.create(
            course=harbor_links,
            name="Harbor Links Championship Course",
            facility_id="24d73934-5205-4b14-b1cc-1f7daeb919a4",
            console_facility_id="baf38b57-7a39-42ce-ab35-9f40bc7d5de8",
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created CourseSchedule {harbor_links_championship_course.name}"
            )
        )

        harbor_links_champcourse_back_9 = CourseSchedule.objects.create(
            course=harbor_links,
            name="Harbor Links ChampCourse Back Nine",
            facility_id="e6b9aa2b-92ca-4021-af9b-9696ea9ddbfc",
            console_facility_id="5f569fa1-d03a-4854-8a8c-44cc2c83fe84",
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created CourseSchedule {harbor_links_champcourse_back_9.name}"
            )
        )
        harbor_links_executive_course = CourseSchedule.objects.create(
            course=harbor_links,
            name="Harbor Links 	Executive Course",
            facility_id="73cf891c-d49d-49e1-820c-63f226440534",
            console_facility_id="04266ec3-23b4-4b7d-8f12-c80e66e38f38",
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created CourseSchedule {harbor_links_executive_course.name}"
            )
        )

        """
        Create UserTeeTimeRequest
        """

        user_request = UserTeeTimeRequest.objects.create(
            user=u,
            course=douglaston,
            date=date(2023, 12, 8),
            players=UserTeeTimeRequest.Players.ANY,
            group_id="weekday_deals",
            status=UserTeeTimeRequest.Status.ACTIVE,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created UserTeeTimeRequest {user_request.id}")
        )
        user_request.course_schedules.set([douglaston_eighteen])

        user_request = UserTeeTimeRequest.objects.create(
            user=u,
            course=kissena,
            date=date(2023, 12, 8),
            players=UserTeeTimeRequest.Players.ANY,
            group_id="weekday_deals",
            status=UserTeeTimeRequest.Status.ACTIVE,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created UserTeeTimeRequest {user_request.id}")
        )
        user_request.course_schedules.set([kissena_eighteen])

        user_request = UserTeeTimeRequest.objects.create(
            user=u,
            course=forest_park,
            date=date(2023, 12, 8),
            players=UserTeeTimeRequest.Players.ANY,
            group_id="weekday_deals",
            status=UserTeeTimeRequest.Status.ACTIVE,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created UserTeeTimeRequest {user_request.id}")
        )
        user_request.course_schedules.set([forest_park_eighteen])

        user_request = UserTeeTimeRequest.objects.create(
            user=u,
            course=bethpage,
            date=date(2024, 9, 27),
            tee_time_max=time(9, 40),
            players=UserTeeTimeRequest.Players.FOUR,
            holes=UserTeeTimeRequest.Holes.EIGHTEEN,
            status=UserTeeTimeRequest.Status.ACTIVE,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created UserTeeTimeRequest {user_request.id}")
        )
        user_request.course_schedules.set(
            [
                bethpage_blue,
                bethpage_green,
                bethpage_red,
                bethpage_black,
            ]
        )

        """

        user_request = UserTeeTimeRequest.objects.create(
            user=u,
            course=douglaston,
            # days=UserTeeTimeRequest.DaysChoices.TODAY,
            date=date(2023, 8, 24),
            search_time_min=time(5, 00),
            search_time_max=time(23, 00),
            search_day=UserTeeTimeRequest.SearchDayChoices.WEEKDAYS,
            status=UserTeeTimeRequest.Status.INACTIVE,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created UserTeeTimeRequest {user_request.id}")
        )
        user_request.course_schedules.set([douglaston_eighteen])

        user_request = UserTeeTimeRequest.objects.create(
            user=u,
            course=kissena,
            # days=UserTeeTimeRequest.DaysChoices.TODAY,
            date=date(2023, 8, 24),
            search_time_min=time(5, 00),
            search_time_max=time(23, 00),
            search_day=UserTeeTimeRequest.SearchDayChoices.WEEKDAYS,
            status=UserTeeTimeRequest.Status.INACTIVE,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created UserTeeTimeRequest {user_request.id}")
        )
        user_request.course_schedules.set([kissena_eighteen])

        user_request = UserTeeTimeRequest.objects.create(
            user=u,
            course=harbor_links,
            date=date(2023, 10, 14),
            tee_time_min=time(11, 59),
            tee_time_max=time(13, 51),
            search_time_min=time(5, 00),
            search_time_max=time(23, 00),
            players=UserTeeTimeRequest.Players.FOUR,
            status=UserTeeTimeRequest.Status.ACTIVE,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created UserTeeTimeRequest {user_request.id}")
        )
        user_request.course_schedules.set([harbor_links_championship_course])

        """
