from timetable import Timetable
from building import *
from timeutils import *
from itertools import product
import os

class TimetableMetrics():
    def __init__(self, timetable, buildings):
        self.table = timetable
        self.buildings = buildings

    def some_metrics(self):
        groups = dict()
        table = self.table

        for event in table.events:
            event.building = get_building(event.room,self.buildings)
            for module in event.modules:
                if event.groups:
                    for module in event.modules:
                        if not module in groups:
                            groups[module] = set()
                        groups[module].update(event.groups)
        for module,group in groups.items():
            groups[module] = sorted(group)
            if not groups[module]:
                groups[module].add(None)#for product to work
        modules = list(groups.keys())



        for combinations in product(*groups.values()):
            #filter out events by group
            days = {day:set() for day in table.days}
            for idx,group in enumerate(combinations):
                filtered = filter( (lambda x:  modules[idx] in x.modules), table.events)
                filtered = filter( (lambda x: (not x.groups) or (group in x.groups)), filtered)
                for event in filtered:
                    days[event.day].add(event)


                for week in range(4,31):
                    events = [list(filter(lambda x:week in x.weeks,events)) for events in days.values()]
                    events = [sorted(x) for x in events if x]
                    if not events:
                        print(week,"free")
                        continue
                    for evs in events:
                        conflict = self.check_conflict(evs)
                        length = minute_to_string(evs[-1].end_time - evs[0].start_time)
                        time = minute_to_string(self.total_time(evs))
                        lunch_dur = self.can_get_lunch(evs)

                        distance = self.total_distance(evs)
                        self.can_walk(evs)
                        print(evs[0].day,combinations,"length:",length,",Total_time:",time,",Conflicts:",conflict,",Distance:",distance,",Lunch:",lunch_dur,"events",len(evs))

    def total_time(self,events):
        t = 0
        for i,event in enumerate(events):
            if not any(event.overlaps(e) for e in events[:i]):
                t += event.end_time-event.start_time
        return t

    def total_distance(self,events):
        distance = [i.building.distance_to(j.building) for i,j in zip(events[:-1],events[1:])]
        distance = [round(x) for x in distance]
        return sum(distance)

    def can_walk(self,events):
        pairs = list(zip(events[:-1],events[1:]))
        times = [j.start_time-i.end_time  + 10 for i,j in pairs] # lectures are 50 mins
        distances = [i.building.distance_to(j.building) for i,j in pairs]
        speeds = [ (distance/time/60) for distance,time in zip(distances,times) ]
        #print(speeds)
        return speeds

    def can_get_lunch(self,events):
        #11:30 to 14:00
        lunchbreak = (690,840)
        s = set(range(*lunchbreak))
        for ev in events:
            s.difference_update(set(range(ev.start_time,ev.end_time+1)))
        s = sorted(s)
        duration = 0
        max_duration = 0
        for i,j in zip(s,s[1:]):
            if i+1 == j:
                duration += 1
            else:
                if max_duration < duration:
                    max_duration = duration
        return max(max_duration,duration)





    def check_conflict(self,events):
        for i,event in enumerate(events[:-1]):
            if any(event.overlaps(e) for e in events[i+1:]):
                return [str(x) for x in events[i+1:] if event.overlaps(x)] + [str(event)]

        return None

        #get all module codes and group combos

    def filter_groups(self,groups):

        return list(filter(groups.isdisjoint,(x.group for x in events)))


if __name__ == "__main__":

    files = ["Room List.xlsx", "Roomequip.xlsx", "Timetable2018-19.xlsx","buildings.csv"]
    paths = [os.path.join("Data",x) for x in files]
    buildings = load_buildings(paths[3])
    rooms = load_rooms(paths[0], paths[1], buildings)
    timetable = Timetable(paths[2])
    modules = timetable.list_modules()

    test = ['CS1']
    events = timetable.generate_event_list(test)
    print(len(events))
    timetable.load_events(events)
    m = TimetableMetrics(timetable,buildings)
    m.some_metrics()

