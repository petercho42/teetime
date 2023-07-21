from teetimebot.models import User, Course, CourseSchedule, UserTeeTimeRequest, ForeUpUser
from datetime import date, datetime

import os
import requests
import time

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

        today_date = date.today()
        print(today_date)
        if user_request.date >= today_date:
            session = requests.session()
            Search.get_fourupsoftware_session(session, user_request)

            while(True):
                # Create a session to handle cookies
                Search.check_for_tee_times(session, user_request)
                break

    @staticmethod
    def check_for_tee_times(session, request_obj):
        for schedule in request_obj.course.courseschedule_set.all():
            data = {
                'time':'all',
                'date':request_obj.date.strftime('%m-%d-%Y'),
                'holes':'all',
                'players':request_obj.players,
                'booking_class':schedule.booking_class,
                'schedule_id':schedule.schedule_id,
                'schedule_ids[]':2517,
                'schedule_ids[]':2431,
                'schedule_ids[]':2433,
                'schedule_ids[]':2539,
                'schedule_ids[]':2538,
                'schedule_ids[]':2434,
                'schedule_ids[]':2432,
                'schedule_ids[]':2435,
                'specials_only':0,
                'api_key':'no_limits'
            }
            try:
                # Make the GET request with data as query parameters
                response = session.get(Search.FOREUP_TIMES_API, params=data)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Process the API response
                    api_data = response.json()
                    # ... Your processing logic here ...

                    for tee_time in api_data:
                        time_obj = datetime.strptime(tee_time['time'], '%Y-%m-%d %H:%M').time()
                        if request_obj.tee_time_min and time_obj <= request_obj.tee_time_min:
                            break
                        if request_obj.tee_time_max and time_obj >= request_obj.tee_time_max:
                            break

                        print(f'Found: {tee_time["schedule_name"]} @{time_obj.strftime("%I:%M %p")} for {tee_time["available_spots"]}')

                else:
                    print(f'Failed to fetch data from the API: {response.status_code} : {response.text}')
            except requests.exceptions.RequestException as e:
                # Handle exceptions such as network errors
                print('Error while making API request:', e)
            time.sleep(2)

    @staticmethod
    def get_fourupsoftware_session(session, request_obj):

        foreup_user = request_obj.user.foreupuser_set.all()[0]
        login_data = {
            'username': foreup_user.username,
            'password': foreup_user.password if foreup_user.password else Search.MY_FOREUP_PASSWORD,
            'booking_class_id': foreup_user.booking_class,
            'api_key': 'no_limits',
            'course_id': foreup_user.course_id,
        }

        # Send the login POST request
        response = session.post(Search.FOREUP_LOGIN_API, data=login_data)

        # Check if login was successful (based on status code or response content)
        if response.status_code == 200:
            # You are now logged in and can access the authenticated pages
            print('Login Success')
        else:
            print(f'Login failed. {response.status_code}: {response.text}')
