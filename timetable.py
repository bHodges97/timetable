import os
import numpy as np
from building import *
from timeutils import *
from yattag import Doc

def matches(string, patterns):
    return any(string.startswith(pattern) for pattern in patterns)

def make_timetable(path,codes):
    days = set()
    start_times = set()
    end_times = set()
    column_headers = set()


    timetable = pyxl.load_workbook(paths[2], read_only = True, data_only = True).active
    for row in timetable.iter_rows(min_row=2,values_only=True):
        module = str(row[1])
        day,time,length,weeks = row[4:8]
        if module and row[0] and row[4]:
            if any(matches(x,codes) for x in module.split(',')):
                end_time = minute_to_time(time_to_minute(time) + str_to_minute(length))
                print(day,time,length,end_time)
                days.add(day)
                times.add(time)
    print(days)
    print(sorted(list(filter(None,times))))


def load_timetable(path):
    timetable = pyxl.load_workbook(paths[2], read_only = True, data_only = True).active
    modules = set()
    for row in timetable.iter_rows(min_row=2,values_only=True):
        module = row[1]
        day,time,length,weeks = row[4:8]
        if module:
            print(module)
            modules.update(module.split(","))



if __name__ == "__main__":
    files = ["Room List.xlsx", "Roomequip.xlsx", "Timetable2018-19.xlsx","buildings.csv"]
    paths = [os.path.join("Data",x) for x in files]

    #buildings = load_buildings(paths[3])
    #rooms = load_rooms(paths[0], paths[1], buildings)

    #timetable = pyxl.load_workbook(paths[2]).active
    make_timetable(paths[2],"CS1")
    #get_info(paths[2])
