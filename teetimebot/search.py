import os
import pickle
import random
import redis
import requests
import time

from datetime import date, datetime, timedelta

from teetimebot.models import Course, MatchingTeeTime, UserTeeTimeRequest
from teetimebot.twilio_client import TwilioClient
from teetimebot.email_client import EmailClient


class Search:
    FOREUP_LOGIN_API = (
        "https://foreupsoftware.com/index.php/api/booking/users/login"  # GET
    )
    FOREUP_TIMES_API = "https://foreupsoftware.com/index.php/api/booking/times"  # POST
    FOREUP_PENDING_RESERVATION_API = (
        "https://foreupsoftware.com/index.php/api/booking/pending_reservation"  # POST
    )
    FOREUP_REFRESH_PEDNING_RESERVATION_API = "https://foreupsoftware.com/index.php/api/booking/refresh_pending_reservation"  # POST
    MY_FOREUP_PASSWORD = os.getenv("MY_FOREUP_PASSWORD")

    TEEOFF_HOT_DEALS_API = "https://www.teeoff.com/api/tee-times/hot-deals-zone"  # POST

    @staticmethod
    def run(vendor):
        user_requests = (
            UserTeeTimeRequest.objects.select_related("course")
            .prefetch_related("course__courseschedule_set", "user__foreupuser_set")
            .filter(
                status=UserTeeTimeRequest.Status.ACTIVE, course__booking_vendor=vendor
            )
            .order_by("date")
        )

        if user_requests:
            session = requests.session()

            while True:
                for user_request in user_requests:
                    user_request.update_status_if_expired()
                    print(f"\n[{datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}]")
                    print(
                        f"Searching {user_request.course.name} [{user_request.date if user_request.date else user_request.days}] times.\ntee_time_min: {user_request.tee_time_min}\ntee_time_max: {user_request.tee_time_max}"
                    )
                    if user_request.search_time():
                        if user_request.status == UserTeeTimeRequest.Status.ACTIVE:
                            if (
                                user_request.course.booking_vendor
                                == Course.BookingVendor.FOREUP
                            ):
                                Search.__get_foreupsoftware_session(
                                    session, user_request
                                )
                                Search.__check_for_foreup_tee_times(
                                    session, user_request
                                )
                            elif (
                                user_request.course.booking_vendor
                                == Course.BookingVendor.TEEOFF
                            ):
                                Search.__check_for_teeoff_tee_times(
                                    session, user_request
                                )
                    else:
                        time.sleep(10)  # user_request.hibernate()

    @staticmethod
    def __check_for_teeoff_tee_times(session, request_obj):
        for target_date in request_obj.target_dates:
            for schedule in request_obj.course.courseschedule_set.all():
                data = {
                    "FacilityId": str(schedule.schedule_id),
                    "PageSize": 100,
                    "PageNumber": 1,
                    "Date": target_date.strftime("%b %d %Y"),
                    "SortBy": "Date",
                    "SortByRollup": "Date",
                    "SortDirection": 0,
                    "SearchType": 1,
                    "View": "List",
                    "HotDealsOnly": True,
                }

                print(f"Searching for {schedule.name} teetime")

                custom_user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36"
                session.headers.update({"User-Agent": custom_user_agent})
                try:
                    response = session.post(Search.TEEOFF_HOT_DEALS_API, data=data)

                    if response.status_code == 200:
                        api_data = response.json()

                        available_tee_times = []  # need for closing old teetimes
                        for tee_time in api_data:
                            if tee_time["available"]:
                                time_obj = datetime.strptime(
                                    tee_time["teeTime"], "%Y-%m-%dT%H:%M:%S"
                                ).time()  # 2023-08-10T12:03:00
                                if (
                                    request_obj.tee_time_min
                                    and time_obj <= request_obj.tee_time_min
                                ):
                                    break
                                if (
                                    request_obj.tee_time_max
                                    and time_obj >= request_obj.tee_time_max
                                ):
                                    break
                                MatchingTeeTime.update_or_create_instance(
                                    request_obj, schedule, tee_time
                                )
                                available_tee_times.append(tee_time["teeTime"])
                        MatchingTeeTime.process_gone_matching_tee_times(
                            request_obj, schedule, target_date, available_tee_times
                        )
                    else:
                        print("Request Headers:")
                        for key, value in response.request.headers.items():
                            print(f"{key}: {value}")
                        print(
                            f"Failed to fetch data from the API: {response.status_code} : {response.text}"
                        )
                except requests.exceptions.RequestException as e:
                    # Handle exceptions such as network errors
                    print("Error while making API request:", e)
        random_sleep_duration = random.randint(1, 60)
        # Sleep for the random duration
        print(f"Sleeping for {random_sleep_duration} seconds")
        time.sleep(random_sleep_duration)

    @staticmethod
    def __check_for_foreup_tee_times(session, request_obj):
        for target_date in request_obj.target_dates:
            for schedule in request_obj.course.courseschedule_set.all():
                print(
                    f"Searching for {schedule.name} teetime ({target_date.strftime('%A %m-%d-%Y')})"
                )
                data = {
                    "time": "all",
                    "date": target_date.strftime("%m-%d-%Y"),
                    "holes": "all",
                    "players": request_obj.players,
                    "booking_class": schedule.booking_class,
                    "schedule_id": schedule.schedule_id,
                    "schedule_ids[]": 2517,  # vanity key value kept to look more inconspicuous
                    "schedule_ids[]": 2431,  # vanity key value
                    "schedule_ids[]": 2433,  # vanity key value
                    "schedule_ids[]": 2539,  # vanity key value
                    "schedule_ids[]": 2538,  # vanity key value
                    "schedule_ids[]": 2434,  # vanity key value
                    "schedule_ids[]": 2432,  # vanity key value
                    "schedule_ids[]": 2435,  # vanity key value
                    "specials_only": 0,
                    "api_key": "no_limits",
                }
                try:
                    # Make the GET request with data as query parameters
                    response = session.get(Search.FOREUP_TIMES_API, params=data)

                    # Check if the request was successful (status code 200)
                    if response.status_code == 200:
                        # Process the API response
                        api_data = response.json()
                        # ... Your processing logic here ...

                        available_tee_times = []  # need for closing old teetimes
                        for tee_time in api_data:
                            time_obj = datetime.strptime(
                                tee_time["time"], "%Y-%m-%d %H:%M"
                            ).time()
                            if (
                                request_obj.tee_time_min
                                and time_obj <= request_obj.tee_time_min
                            ):
                                break
                            if (
                                request_obj.tee_time_max
                                and time_obj >= request_obj.tee_time_max
                            ):
                                break
                            pending_reservation_data = {
                                "time": tee_time["time"],
                                "holes": tee_time["holes"],
                                "players": tee_time["available_spots"],
                                "carts": "false",
                                "schedule_id": tee_time["schedule_id"],
                                "teesheet_side_id": tee_time["teesheet_side_id"],
                                "course_id": tee_time["course_id"],
                                "booking_class_id": tee_time["booking_class_id"],
                                "duration": 1,
                            }
                            print(pending_reservation_data)
                            headers = {"Api-Key": "no_limits"}
                            response = session.post(
                                Search.FOREUP_PENDING_RESERVATION_API,
                                data=pending_reservation_data,
                                headers=headers,
                            )
                            if response.status_code == 200:
                                reservation_id = response.json()["reservation_id"]
                                print(f"Created pending reservation {reservation_id}")
                                MatchingTeeTime.update_or_create_instance(
                                    request_obj, schedule, tee_time
                                )
                                available_tee_times.append(tee_time["time"])
                                refresh_left = 5  # refresh pending reservation 5 times, 15 seconds each.
                                while refresh_left > 0:
                                    time.sleep(15)
                                    response = session.post(
                                        f"{Search.FOREUP_REFRESH_PEDNING_RESERVATION_API}/{reservation_id}",
                                        headers=headers,
                                    )
                                    if response.status_code == 200:
                                        print(f"Pending Reservation Refresh Success")
                                    else:
                                        print(
                                            f"Failed to refresh pending reservation: {response.status_code} : {response.text}"
                                        )
                                    refresh_left = refresh_left - 1
                                response = session.delete(
                                    f"{Search.FOREUP_PENDING_RESERVATION_API}/{reservation_id}",
                                    headers=headers,
                                )
                                if response.status_code == 200:
                                    print(f"Pending Reservation Delete Success")
                                else:
                                    print(
                                        f"Failed to delete pending reservation: {response.status_code} : {response.text}"
                                    )
                            else:
                                print(
                                    f"Failed to create pending reservation: {response.status_code} : {response.text}"
                                )
                        MatchingTeeTime.process_gone_matching_tee_times(
                            request_obj, schedule, request_obj.date, available_tee_times
                        )
                    else:
                        print(
                            f"Failed to fetch data from the API: {response.status_code} : {response.text}"
                        )
                except requests.exceptions.RequestException as e:
                    # Handle exceptions such as network errors
                    print("Error while making API request:", e)
                # randomly sleep for 1-5 seconds to avoid getting rate limited
                random_float = round(random.uniform(1, 5), 1)
                time.sleep(random_float)

    @staticmethod
    def __get_foreupsoftware_session(session, request_obj):
        redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
        session_key = (
            f"user:{request_obj.user.id}:course:{request_obj.course.id}:login_session"
        )
        serialized_session = redis_client.get(session_key)
        if serialized_session is not None:
            session_data = pickle.loads(serialized_session)
            # print(f'Session key {session_key} taken from redis')
            # Set session data in the new session object
            for cookie_name, cookie_value in session_data["cookies"].items():
                session.cookies.update({cookie_name: cookie_value})
        else:
            foreup_user = request_obj.user.foreupuser_set.all()[0]
            login_data = {
                "username": foreup_user.username,
                "password": foreup_user.password
                if foreup_user.password
                else Search.MY_FOREUP_PASSWORD,
                "booking_class_id": foreup_user.booking_class,
                "api_key": "no_limits",
                "course_id": foreup_user.course_id,
            }

            # Send the login POST request
            response = session.post(Search.FOREUP_LOGIN_API, data=login_data)

            # Check if login was successful (based on status code or response content)
            if response.status_code == 200:
                # You are now logged in and can access the authenticated pages
                print("Login Success. Saving the serialized session to redis")
                session_data = {
                    "cookies": session.cookies.get_dict(),
                    # Add any other necessary session data here
                }
                serialized_session = pickle.dumps(session_data)
                redis_client.set(session_key, serialized_session)
            else:
                print(f"Login failed. {response.status_code}: {response.text}")
