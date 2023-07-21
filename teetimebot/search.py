from teetimebot.models import User, Course, CourseSchedule, UserTeeTimeRequest, ForeUpUser
from datetime import date, datetime

import os
import requests

class Search:

    FOREUP_LOGIN_API = 'https://foreupsoftware.com/index.php/api/booking/users/login' # GET
    FOREUP_TIMES_API = 'https://foreupsoftware.com/index.php/api/booking/times' # POST
    MY_FOREUP_PASSWORD = os.getenv('MY_FOREUP_PASSWORD')

    @staticmethod
    def run():
        user_request = UserTeeTimeRequest.objects.select_related(
                'course'
            ).prefetch_related(
                'course__courseschedule_set', 'user__foreupuser_set'
            ).filter(
                date__gte= date.today(),
                status=UserTeeTimeRequest.Status.ACTIVE,
            )[0]
        
        print(user_request.date)
        print(f'tee_time_min: {user_request.tee_time_min}')
        print(f'tee_time_max: {user_request.tee_time_max}')
        print(user_request.course.name)
        print(user_request.course.courseschedule_set.all())

        today_date = date.today()
        print(today_date)
        if user_request.date >= today_date:
            while(True):
                Search.call_fourupsoftware(user_request)
                break


    @staticmethod
    def call_fourupsoftware(request_obj):
        foreup_user = request_obj.user.foreupuser_set.all()[0]
        login_data = {
            'username': foreup_user.username,
            'password': foreup_user.password if foreup_user.password else Search.MY_FOREUP_PASSWORD,
            'booking_class_id': foreup_user.booking_class,
            'api_key': 'no_limits',
            'course_id': foreup_user.course_id,
        }

        # Create a session to handle cookies
        session = requests.session()

        # Send the login POST request
        response = session.post(Search.FOREUP_LOGIN_API, data=login_data)

        # Check if login was successful (based on status code or response content)
        if response.status_code == 200:
            # You are now logged in and can access the authenticated pages
            print('Login Success')
        else:
            print(f'Login failed. {response.status_code}: {response.text}')
        '''
        user = models.ForeignKey(User, on_delete=models.PROTECT)
        course = models.ForeignKey(Course, on_delete=models.PROTECT)
        date = models.DateField()
        tee_time_min = models.TimeField(default=None, null=True, blank=True)
        tee_time_max = models.TimeField(default=None, null=True, blank=True)
        players = models.IntegerField(choices=Players.choices, default=Players.ANY)
        holes = models.CharField(
            max_length=20,
            choices=Holes.choices,
            default=Holes.ANY,
        )
        status = models.CharField(
            max_length=20,
            choices=Status.choices,
            default=Status.INACTIVE,
        )
        '''
