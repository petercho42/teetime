from django.core.management.base import BaseCommand
from teetimebot.email_client import EmailClient


class Command(BaseCommand):
    help = "Simple script to test email in dev"

    """
    def add_arguments(self, parser):
        parser.add_argument("course_ids", nargs="+", type=int)
    """

    def handle(self, *args, **options):
        """
        Clean Data
        """
        EmailClient.send_email_with_outlook(
            "monkeydluffy1p1p@gmail.com", "subject", "body"
        )
        self.stdout.write(self.style.SUCCESS(f"Test Done"))
