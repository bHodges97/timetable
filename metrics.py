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

        for combination in product(*groups.values()):
            #filter out events by group
            days = {day:set() for day in table.days}
            scores2 = []
            for idx,group in enumerate(combination):
                filtered = filter( (lambda x:  modules[idx] in x.modules), table.events)
                filtered = filter( (lambda x: (not x.groups) or (group in x.groups)), filtered)
                for event in filtered:
                    days[event.day].add(event)

                scores = []
                conflict = None
                for week in range(4,31):
                    events = [list(filter(lambda x:week in x.weeks,events)) for events in days.values()]
                    events = [sorted(x) for x in events]
                    if conflict:
                        print("Conflict:",conflict)
                        scores = []
                        break

                    if not events:
                        continue
                    score = np.zeros((7,6))
                    for i,evs in enumerate(events):
                        if not evs:
                            continue
                        conflict = self.check_conflict(evs)
                        wait_times = [j.start_time-i.end_time for i,j in zip(evs[:-1],evs[1:])]
                        distances = [i.building.distance_to(j.building) for i,j in zip(evs[:-1],evs[1:])]
                        wait_time = 0 if not wait_times else round(sum(wait_times)/len(wait_times))
                        lec_time = sum(x.length_time for x in evs)
                        day_length = evs[-1].end_time - evs[0].start_time
                        lunch_dur = self.lunch_time(evs)
                        speeds = [(distance/(time+10)/60) for distance,time in zip(distances,wait_times)] # include 10 mins for lec end
                        speed = 0 if not speeds else max(speeds)
                        timing = self.good_time_of_day(evs)

                        score[i,:] = wait_time,lec_time,day_length,lunch_dur,speed,timing
                    scores.append(score)
            scores2.append(scores)
        for b in scores2[0]:
            print(b)



    def lunch_time(self,events):
        #11:30 to 14:00
        lunchbreak = (690,841)
        s = set(range(*lunchbreak))
        for ev in events:
            s.difference_update(set(range(ev.start_time+1,ev.end_time)))
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


    def good_time_of_day(self,events):
        start = 10 * 60 # 10 am
        end = 15 * 60 # 3 pm
        score = 0
        if events[0].start_time >= start:
            score += 1
        if events[-1].end_time <= end:
            score += 1
        return score



if __name__ == "__main__":

    files = ["Room List.xlsx", "Roomequip.xlsx", "Timetable2018-19.xlsx","buildings.csv"]
    paths = [os.path.join("Data",x) for x in files]
    buildings = load_buildings()
    #rooms = load_rooms(paths[0], paths[1], buildings)
    timetable = Timetable(paths[2])
    modules = timetable.list_modules()

    test = ['CS1']
    events = timetable.generate_event_list(test)
    timetable.load_events(events)
    m = TimetableMetrics(timetable,buildings)
    m.some_metrics()
