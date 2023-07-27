import os
from twilio.rest import Client


class TwilioClient:

    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twilio_number = '+18669141114'
    client = Client(account_sid, auth_token)


    @staticmethod
    def send_message(to_phonenumber, body):
        message = TwilioClient.client.messages \
                        .create(
                            body=body,
                            from_=TwilioClient.twilio_number,
                            to=to_phonenumber
                        )

        print(message.sid)