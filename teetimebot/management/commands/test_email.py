from django.core.management.base import BaseCommand, CommandError
from datetime import date, time
from teetimebot.email_client import EmailClient
from teetimebot.models import User, Course, CourseSchedule, UserTeeTimeRequest, ForeUpUser
from teetimebot.search import Search

from phonenumber_field.phonenumber import PhoneNumber



class Command(BaseCommand):
    help = "Simple script to test email in dev"

    """
    def add_arguments(self, parser):
        parser.add_argument("course_ids", nargs="+", type=int)
    """

    def handle(self, *args, **options):
        '''
        Clean Data
        '''
        EmailClient.send_email_with_yahoo("phcho83@gmail.com", "subject", "body")
        self.stdout.write(
            self.style.SUCCESS(f'Test Done')
        )