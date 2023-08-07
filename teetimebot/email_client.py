import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailClient:
    YAHOO_SMTP_SERVER = "smtp.mail.yahoo.com"
    YAHOO_SMTP_PORT = 587

    YAHOO_SENDER_EMAIL = os.environ["YAHOO_SENDER_EMAIL"]
    YAHOO_SENDER_PASSWORD = os.environ["YAHOO_SENDER_PASSWORD"]

    OUTLOOK_SMTP_SERVER = "smtp-mail.outlook.com"
    OUTLOOK_SMTP_PORT = 587
    OUTLOOK_SENDER_EMAIL = "petercho42@gmail.com"  # os.environ['OUTLOOK_SENDER_EMAIL']
    OUTLOOK_SENDER_PASSWORD = os.environ["OUTLOOK_SENDER_PASSWORD"]

    @staticmethod
    def send_email_with_yahoo(receiver_email, subject, body):
        message = MIMEMultipart()
        message["From"] = EmailClient.YAHOO_SENDER_EMAIL
        message["To"] = receiver_email
        message["Subject"] = subject

        # Attach the body of the email
        message.attach(MIMEText(body, "plain"))

        try:
            raise Exception("Not implemented yet")
            with smtplib.SMTP(
                EmailClient.YAHOO_SMTP_SERVER, EmailClient.YAHOO_SMTP_PORT
            ) as server:
                server.starttls()
                server.login(
                    EmailClient.YAHOO_SENDER_EMAIL, EmailClient.YAHOO_SENDER_PASSWORD
                )
                server.sendmail(
                    EmailClient.YAHOO_SENDER_EMAIL, receiver_email, message.as_string()
                )
            print("Email sent successfully.")
        except Exception as e:
            print(f"Yahoo Error: {str(e)}")

    @staticmethod
    def send_email_with_outlook(receiver_email, subject, body):
        message = MIMEMultipart()
        message["From"] = EmailClient.OUTLOOK_SENDER_EMAIL
        message["To"] = receiver_email
        message["Subject"] = subject

        # Attach the body of the email
        message.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(
                EmailClient.OUTLOOK_SMTP_SERVER, EmailClient.OUTLOOK_SMTP_PORT
            ) as server:
                server.starttls()
                server.login(
                    EmailClient.OUTLOOK_SENDER_EMAIL,
                    EmailClient.OUTLOOK_SENDER_PASSWORD,
                )
                server.sendmail(
                    EmailClient.OUTLOOK_SENDER_EMAIL,
                    receiver_email,
                    message.as_string(),
                )
            print("Email sent successfully.")
        except Exception as e:
            print(f"Outlook Error: {str(e)}")
            raise
