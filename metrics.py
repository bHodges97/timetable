from timetable import Timetable
from building import *
import os

class TimetableMetrics():
    def __init__(self, timetable, buildings):
        self.table = timetable
        self.buildings = buildings

    def some_metrics(self):
        groups = dict()

        for event in table.events:
            for module in event.modules:
                if not module in groups:
                    groups[module] = set()
                if event.group:
                    for module in event.modules:
                        groups[module].update(event.group)

        print(groups.values())
        for i in table.days["Mon"]:
            print(i.start_time)
        #get all module codes and group combos



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
    m = TimetableMetrics(timetable,buildings)
    m.some_metrics(buildings)

