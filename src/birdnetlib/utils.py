import calendar
import math


def return_week_48_from_datetime(dt):
    day_of_year = dt.timetuple().tm_yday
    days_in_year = 366 if calendar.isleap(dt.year) else 365
    week_48 = math.ceil((day_of_year / days_in_year) * 48)
    return week_48
