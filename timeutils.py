from datetime import time,datetime

def str_to_minute(string):
    time = datetime.strptime(string,"%H:%M")
    return time_to_minute(time)

def time_to_minute(time):
    return time.hour * 60 + time.minute

def minute_to_time(minute):
    return time(hour = (minute // 60), minute = (minute % 60))

def minute_to_string(minute):
    return minute_to_time(minute).strftime("%H:%M")
