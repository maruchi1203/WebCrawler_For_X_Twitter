import sys, os
from datetime import datetime, timedelta
import calendar

def parse_time_for_korea(text_date: str):
    date, time = text_date.split("T")

    year, month, day = date.split("-")
    hour, minute, second = time.split(":")

    ret_date = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second[:-5]))
    # ret_date = ret_date + timedelta(hours=7)

    return ret_date


def parse_date(date: str | datetime):
    if type(date) is datetime:
        date.hour = 0
        date.minute = 0
        date.second = 0
        date.microsecond = 0

        return date

    da = None
    if " " in date:
        d = date.split(" ")
        da = list(map(lambda x: x[:-1], d))
    elif "-" in date:
        d = date.split("-")
        da = d

    parsed_date = list(map(int, da))
    ret_date = datetime(parsed_date[0], parsed_date[1], parsed_date[2])

    return ret_date


def resource_path(file, relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(file)))
    return os.path.join(base_path, relative_path)
