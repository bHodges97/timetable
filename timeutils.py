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

def set_to_range(a):
    a = sorted(a) + [0]#ensures last term is include
    out = []
    start = a[0]
    for x,y in zip(a,a[1:]):
        if x+1 != y:
            s = str(start)
            if start != x:
                s+="-"+str(x)
            out.append(s)
            start=y
    return ",".join(out)

if __name__ == "__main__":
    a = {-1,1,2,3,5,6,8,10,11,13}
    print(set_to_range(a))
    a = set()
    print(set_to_range(a))
