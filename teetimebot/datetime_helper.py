from datetime import date, datetime, time, timedelta


def get_next_dates(days):
    allowed_inputs = ["every_day", "weekdays", "weekends"]

    if days not in allowed_inputs:
        raise ValueError(f"Invalid input: {days}")

    dates = []
    current_date = date.today()
    num_days = 8 if datetime.now().time() >= time(18, 59, 0) else 7
    while num_days > 0:
        if days == "every_day":
            dates.append(current_date)
        elif days == "weekdays":
            current_weekday = current_date.weekday()
            if current_weekday < 5:  # Monday to Friday
                dates.append(current_date)
        elif days == "weekends":
            current_weekday = current_date.weekday()
            if current_weekday > 4:  # Saturday and Sunday
                dates.append(current_date)
        current_date += timedelta(days=1)
        num_days -= 1
    return dates
