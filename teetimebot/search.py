from teetimebot.models import User, Course, CourseSchedule, UserTeeTimeRequest, ForeUpUser
from datetime import datetime

import os
import pickle
import redis
import requests
import time

class Search:

    FOREUP_LOGIN_API = 'https://foreupsoftware.com/index.php/api/booking/users/login' # GET
    FOREUP_TIMES_API = 'https://foreupsoftware.com/index.php/api/booking/times' # POST
    MY_FOREUP_PASSWORD = os.getenv('MY_FOREUP_PASSWORD')

    @staticmethod
    def run():
        user_requests = UserTeeTimeRequest.objects.select_related(
                'course'
            ).prefetch_related(
                'course__courseschedule_set', 'user__foreupuser_set'
            ).filter(
                status=UserTeeTimeRequest.Status.ACTIVE,
            ).order_by('date')
        
        for user_request in user_requests:
            user_request.update_status_if_expired()
            if user_request.status == UserTeeTimeRequest.Status.ACTIVE:
                print(f'{user_request.course.name} Search')
                print(f'date: {user_request.date}')
                print(f'tee_time_min: {user_request.tee_time_min}')
                print(f'tee_time_max: {user_request.tee_time_max}')

                session = requests.session()
                Search.__get_foreupsoftware_session(session, user_request)
                Search.__check_for_tee_times(session, user_request)
                    

    @staticmethod
    def __check_for_tee_times(session, request_obj):
        for schedule in request_obj.course.courseschedule_set.all():
            print(f'Searching for {schedule.name} teetime')
            data = {
                'time':'all',
                'date':request_obj.date.strftime('%m-%d-%Y'),
                'holes':'all',
                'players':request_obj.players,
                'booking_class':schedule.booking_class,
                'schedule_id':schedule.schedule_id,
                'schedule_ids[]':2517, # vanity key value kept to look more inconspicuous 
                'schedule_ids[]':2431, # vanity key value
                'schedule_ids[]':2433, # vanity key value
                'schedule_ids[]':2539, # vanity key value
                'schedule_ids[]':2538, # vanity key value
                'schedule_ids[]':2434, # vanity key value
                'schedule_ids[]':2432, # vanity key value
                'schedule_ids[]':2435, # vanity key value
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
            time.sleep(1.5)

    @staticmethod
    def __get_foreupsoftware_session(session, request_obj):
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        session_key = f'user:{request_obj.user.id}:course:{request_obj.course.id}:login_session'
        print(session_key)
        serialized_session = redis_client.get(session_key)
        if serialized_session is not None:
            session_data = pickle.loads(serialized_session)
            print(f'Session key {session_key} taken from redis')
            # Set session data in the new session object
            for cookie_name, cookie_value in session_data['cookies'].items():
                print(f'{cookie_name}: {cookie_value}')
                session.cookies.update({cookie_name: cookie_value})
        else:
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
                print('Login Success. Saving the serialized session to redis')
                print(session.cookies)
                session_data = {
                    'cookies': session.cookies.get_dict(),
                    # Add any other necessary session data here
                }
                serialized_session = pickle.dumps(session_data)
                redis_client.set(session_key, serialized_session)
            else:
                print(f'Login failed. {response.status_code}: {response.text}')
