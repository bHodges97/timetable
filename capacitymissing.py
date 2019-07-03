from timetable import Timetable
from building import *
import os


if __name__ == "__main__":

    files = ["Room List.xlsx", "Roomequip.xlsx", "Timetable2018-19.xlsx","buildings.csv"]
    paths = [os.path.join("Data",x) for x in files]
    buildings = load_buildings(paths[3])
    _rooms = load_rooms(paths[0], paths[1], buildings)
    timetable = Timetable(paths[2])
    rooms = set()
    for row in timetable.timetable.iter_rows(min_row=2,values_only=True):
        if row[8]:
            rooms.update(row[8].split(','))

    with open('capacitymissing.txt','w') as f:
        for room in rooms:
            if room not in _room:
                f.write(str(room)+'\n')

