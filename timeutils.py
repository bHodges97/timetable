import datetime as dt
from datetime import datetime

def str_to_minute(string):
    time = datetime.strptime(string,"%H:%M")
    return time_to_minute(time)

def time_to_minute(time):
    return time.hour * 60 + time.minute

def minute_to_time(minute):
    return dt.time(hour = (minute // 60), minute = (minute % 60))
