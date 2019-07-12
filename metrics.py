from timetable import Timetable
from building import *
from timeutils import *
from itertools import product
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import os

class TimetableMetrics():
    def __init__(self, timetable, buildings,name):
        self.table = timetable
        self.buildings = buildings
        self.name = name

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
        self.modules = list(groups.keys())

        scores2 = []
        for combination in product(*groups.values()):
            #filter out events by group
            days = {day:set() for day in table.days}
            for idx,group in enumerate(combination):
                filtered = filter( (lambda x:  self.modules[idx] in x.modules), table.events)
                filtered = filter( (lambda x: (not x.groups) or (group in x.groups)), filtered)
                for event in filtered:
                    days[event.day].add(event)
                scores = []
                conflict = None

                for week in range(5,15):
                    events = [list(filter(lambda x:week in x.weeks,events)) for events in days.values()]
                    events = [sorted(x) for x in events]
                    if not events:
                        continue

                    score = np.zeros((7,5))
                    for i,evs in enumerate(events):
                        if not evs:
                            continue
                        conflict = self.check_conflict(evs)
                        wait_times = [j.start_time-i.end_time for i,j in zip(evs[:-1],evs[1:])]
                        distances = [i.building.distance_to(j.building) for i,j in zip(evs[:-1],evs[1:])]
                        wait_time = 0 if not wait_times else round(sum(wait_times)/len(wait_times))
                        speeds = [(distance/(time+10)/60) for distance,time in zip(distances,wait_times)] # include 10 mins for lec end
                        speed = 0 if not speeds else max(speeds)
                        timing = self.good_time_of_day(evs)

                        speedscore = 20 - min(20,speed/5 * 20)
                        lunch =   min(self.lunch_time(evs), 45) / 45 * 20
                        wtime  = 20 if wait_time <= 60 else max(0,20 - (wait_time-60)/30 * 5)
                        dl = self.daylength(evs)
                        mets = (wtime,speedscore,lunch,timing,dl)
                        score[i,:] = mets

                    if conflict:
                        print("Conflict:",conflict)
                        scores = []
                        break
                    for (s,weeks) in scores:
                        if np.array_equal(s,score):
                            weeks.add(week)
                            break
                    else:
                        scores.append((score,{week}))
                scores = [(score,set_to_range(week),self.score_of_matrix(score)) for score,week in scores]
                #print(len(scores),min(x[2] for x in scores if x[2]))
            scores2.append((scores,combination))
        scores2 = [x for x in scores2 if x[0]]
        print(len(scores2))
        return scores2

    def score_of_matrix(self,m):
        count = np.count_nonzero(np.count_nonzero(m,axis=1))
        return 0 if count == 0 else np.sum(m)/count


    def average(self,scores):
        out = np.zeros((7,5))
        scores = np.stack(scores,axis=0)
        day_scores = np.sum(scores,axis=0)
        counts = np.array(scores)
        counts[counts>1] = 1
        counts = np.sum(counts,axis=0)
        np.divide(day_scores,counts,out=out,where=counts!=0)
        return out

    def plot_it(self,scores):
        every = []
        for s,_ in scores:
            every += [x[0] for x in s]
        avg_every = self.average(every)
        self.plot_week(avg_every,title="Average score:" , name=(self.name+"-average"))
        print("Avg score: ",self.score_of_matrix(avg_every))


        mscore = 100 * 7
        bscore = 0
        combo_worst = mscore
        combo_best = 0

        for y in scores:
            s,c = y
            m = [x[0] for x in s]
            avg = self.average(m)
            combo_score = self.score_of_matrix(avg)
            if combo_worst > combo_score:
                combo_worst = combo_score
                combo_worst_name = c
                combo_worst_m = avg
            if combo_best < combo_score:
                combo_best = combo_score
                combo_best_name = c
                combo_best_m = avg
            for x,w,score in s:
                if score < mscore and score > 0:
                    mscore = score
                    matrix,week,combo = x,w,c
                if score > bscore:
                    bscore = score
                    bmatrix,bweek,bcombo = x,w,c

        print("Worst score:",mscore,list(zip(self.modules,combo)),week)
        print("Best score:",bscore,list(zip(self.modules,bcombo)),bweek)
        print("Worst combination avg:",combo_worst,list(zip(self.modules,combo_worst_name)))
        print("Best combination avg:",combo_best,list(zip(self.modules,combo_best_name)))
        self.plot_week(matrix,title="Worst score: week "+week,name=self.name+"-worst")
        self.plot_week(matrix,title="Best score: week "+bweek,name=self.name+"-best")
        self.plot_week(combo_best_m,title="Best combo:\n "+str(list(zip(self.modules,combo_best_name))),name=self.name+"-bestcombo")
        self.plot_week(combo_worst_m,title="Worst combo:\n "+str(list(zip(self.modules,combo_worst_name))),name=self.name+"-worstcombo")


    def plot_week(self,matrix,title="Happiness Scores",name="output"):
        plt.clf()
        N = 7
        ind = np.arange(N)    # the x locations for the groups
        width = 0.35       # the width of the bars: can also be len(x) sequence
        plts= [plt.bar(ind, matrix[:,0], width)]
        plts+=[plt.bar(ind, matrix[:,i], width,bottom=np.sum(matrix[:,:i],axis=1)) for i in range(1,5)]
        plt.ylabel('Scores')
        plt.title(title)
        plt.xticks(ind, ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat','Sun'))
        plt.yticks(np.arange(0, 110, 10))
        plt.legend(plts, ('wait time','walking distance','lunch break','time of day','day length',))
        plt.savefig(Path('plots/'+name))

    def lunch_time(self,events):
        #12:00 to 13:30
        lunchbreak = (720,811)
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
            score += 10
        if events[-1].end_time <= end:
            score += 10
        return score

    def daylength(self,events):
        score = 0
        if events[-1].end_time - events[0].start_time < 6 * 60:
            score += 10
        if sum(x.length_time for x in events) < 4*60:
            score += 10
        return score



if __name__ == "__main__":

    files = ["Room List.xlsx", "Roomequip.xlsx", "Timetable2018-19.xlsx","buildings.csv"]
    paths = [os.path.join("Data",x) for x in files]
    buildings = load_buildings()
    #rooms = load_rooms(paths[0], paths[1], buildings)
    timetable = Timetable(paths[2])
    modules = timetable.list_modules()

    test = sys.argv[1:]
    events = timetable.generate_event_list(test)
    timetable.load_events(events)
    m = TimetableMetrics(timetable,buildings,'CS1')
    a = m.some_metrics()
    m.plot_it(a)
