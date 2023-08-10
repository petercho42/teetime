from datetime import date, datetime, time, timedelta


def get_next_dates():
    dates = []
    current_date = date.today()
    num_days = 8 if datetime.now().time() >= time(19, 0, 0) else 7
    while len(dates) < num_days:
        dates.append(current_date)
        current_date += timedelta(days=1)
    return dates


def get_next_weekday_dates():
    weekday_dates = []
    current_date = date.today()
    num_days = 6 if datetime.now().time() >= time(19, 0, 0) else 5
    while len(weekday_dates) < num_days:
        current_weekday = current_date.weekday()
        if current_weekday < 5:  # Monday to Friday
            weekday_dates.append(current_date)
        current_date += timedelta(days=1)
    return weekday_dates


def get_next_weekend_dates():
    weekend_dates = []
    current_date = date.today()
    num_days = 3 if datetime.now().time() >= time(19, 0, 0) else 2
    while len(weekend_dates) < num_days:
        current_weekday = current_date.weekday()
        if current_weekday > 4:  # Saturday and Sunday
            weekend_dates.append(current_date)
        current_date += timedelta(days=1)
    return weekend_dates
