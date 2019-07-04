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

    test = ['CS1']
    events = timetable.generate_event_list(test)
    timetable.load_events(events)
    timetable.some_metrics(events, buildings)
