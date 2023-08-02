from django.core.management.base import BaseCommand, CommandError
from datetime import date, time
from teetimebot.models import User, Course, CourseSchedule, UserTeeTimeRequest, ForeUpUser
from teetimebot.search import Search

from phonenumber_field.phonenumber import PhoneNumber


class Command(BaseCommand):
    help = "Simple script to test search in dev"

    def add_arguments(self, parser):
        parser.add_argument('--vendor', type=str, help='The name of the vendor')

    def handle(self, *args, **options):
        vendor = options['vendor']
        if vendor:
            if vendor.lower() == Course.BookingVendor.FOREUP.lower():
                Search.run(Course.BookingVendor.FOREUP)
            elif vendor.lower() == Course.BookingVendor.TEEOFF.lower():
                Search.run(Course.BookingVendor.TEEOFF)
            else:
                self.stdout.write(self.style.ERROR(f'Unknown vendor: {vendor}'))
            self.stdout.write(self.style.SUCCESS('Search Done'))
        else:
            self.stdout.write(self.style.ERROR('Vendor required. E.g. "python manage.py test_run --vender foreup")'))