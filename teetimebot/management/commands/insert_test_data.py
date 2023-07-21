from django.core.management.base import BaseCommand, CommandError
from datetime import date, time
from teetimebot.models import User, Course, CourseSchedule, UserTeeTimeRequest, ForeUpUser

from phonenumber_field.phonenumber import PhoneNumber


class Command(BaseCommand):
    help = "Creates preminary data for testing purpose"

    """
    def add_arguments(self, parser):
        parser.add_argument("course_ids", nargs="+", type=int)
    """

    def handle(self, *args, **options):
        '''
        Clean Data
        '''
        UserTeeTimeRequest.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted All UserTeeTimeRequest Data')
        )
        ForeUpUser.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted All ForeUpUser Data')
        )
        User.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted All User Data')
        )
        CourseSchedule.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted All CourseSchedule Data')
        )
        Course.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted All Course Data')
        )

        '''
        Create User
        '''
        u = User.objects.create(
            first_name = "Peter",
            last_name = "Cho",
            phone_number = PhoneNumber.from_string("+19172820312")
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created User {u.phone_number}')
        )

        '''
        Create ForeUpUser
        '''

        foreup_u = ForeUpUser.objects.create(
            user = u,
            username = "phcho83@gmail.com",
            password = "",  # real password required
            course_id = 19765,
            booking_class=2144
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created ForeUpUser {foreup_u.username}')
        )

        '''
        Create Course
        '''
        bethpage = Course.objects.create(
            name='Bethpage State Park',
            booking_vendor=Course.BookingVendor.FOREUP,
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created Course {bethpage.name}')
        )


        '''
        Create CourseSchedule
        '''
        bethpage_black = CourseSchedule.objects.create(
            course=bethpage,
            name="Bethpage Black Course",
            schedule_id=2431,
            booking_class=2136
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created CourseSchedule {bethpage_black.name}')
        )

        bethpage_red = CourseSchedule.objects.create(
            course=bethpage,
            name="Bethpage Red Course",
            schedule_id=2432,
            booking_class=2138
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created CourseSchedule {bethpage_red.name}')
        )

        bethpage_blue = CourseSchedule.objects.create(
            course=bethpage,
            name="Bethpage Blue Course",
            schedule_id=2433,
            booking_class=2140
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created CourseSchedule {bethpage_blue.name}')
        )

        bethpage_green = CourseSchedule.objects.create(
            course=bethpage,
            name="Bethpage Green Course",
            schedule_id=2434,
            booking_class=2142
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created CourseSchedule {bethpage_green.name}')
        )

        bethpage_yellow = CourseSchedule.objects.create(
            course=bethpage,
            name="Bethpage Yellow Course",
            schedule_id=2435,
            booking_class=2144
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created CourseSchedule {bethpage_yellow.name}')
        )

        '''
        Create UserTeeTimeRequest
        '''
        user_request = UserTeeTimeRequest.objects.create(
            user=u,
            course=bethpage,
            date=date(2023, 7, 22),
            tee_time_min = None,
            tee_time_max = time(8, 00),
            players = UserTeeTimeRequest.Players.ANY,
            holes=UserTeeTimeRequest.Holes.ANY,
            status=UserTeeTimeRequest.Status.ACTIVE
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created UserTeeTimeRequest {user_request.id}')
        )

        user_request = UserTeeTimeRequest.objects.create(
            user=u,
            course=bethpage,
            date=date(2023, 7, 23),
            tee_time_min = None,
            tee_time_max = time(8, 00),
            players = UserTeeTimeRequest.Players.ANY,
            holes=UserTeeTimeRequest.Holes.ANY,
            status=UserTeeTimeRequest.Status.ACTIVE
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created UserTeeTimeRequest {user_request.id}')
        )