from django.core.management.base import BaseCommand
from teetimebot.models import Course
from teetimebot.search import Search


class Command(BaseCommand):
    help = "Simple script to test search in dev"

    def add_arguments(self, parser):
        parser.add_argument("--vendor", type=str, help="The name of the vendor")

    def handle(self, *args, **options):
        vendor = options["vendor"]
        if vendor:
            if vendor.lower() == Course.BookingVendor.FOREUP.lower():
                Search.run(Course.BookingVendor.FOREUP)
            elif vendor.lower() == Course.BookingVendor.TEEOFF.lower():
                Search.run(Course.BookingVendor.TEEOFF)
            elif vendor.lower() == Course.BookingVendor.GOIBSVISION.lower():
                Search.run(Course.BookingVendor.GOIBSVISION)
            else:
                self.stdout.write(self.style.ERROR(f"Unknown vendor: {vendor}"))
            self.stdout.write(self.style.SUCCESS("Search Done"))
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Vendor required. E.g. "python manage.py test_run --vender foreup")'
                )
            )
