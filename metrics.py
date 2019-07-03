from timetable import Timetable
from building import *
import os


if __name__ == "__main__":

    files = ["Room List.xlsx", "Roomequip.xlsx", "Timetable2018-19.xlsx","buildings.csv"]
    paths = [os.path.join("Data",x) for x in files]
    buildings = load_buildings(paths[3])
    rooms = load_rooms(paths[0], paths[1], buildings)
    timetable = Timetable(paths[2])
    modules = timetable.list_modules()

    test = ['CS1PR']
    events = timetable.generate_event_list(test)
    course_rooms = set()
    for row in timetable.timetable.iter_rows(min_row=2,values_only=True):
        if row[0] in events:
            if row[8]:
                course_rooms.update(row[8].split(','))
    course_rooms = sorted(course_rooms)

    for room in course_rooms:
        if room in rooms:
            print(rooms[room].building)
        else:
            print("Missing room info for",room,"guess:",get_building(room,buildings))


