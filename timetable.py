import os
import numpy as np
from building import *
from timeutils import *
from yattag import Doc
from yattag import indent


class Event:
    def __init__(self,row):
        self.id = row[0]
        self.modules = row[1]
        self.type = row[2]
        self.group = row[3]
        self.day = row[4]
        self.time = row[5]
        self.length = row[6]
        self.weeks = row[7]
        self.room = row[8]
        self.string_data = row[9]
        self.room_pool = row[10]
        self.notes = row[11]
        self.details = row[12]

        self.start_time = time_to_minute(self.time)
        self.end_time = self.start_time + str_to_minute(self.length)
        self._modules = self.modules.split(',')

    def __lt__(self, other):
        return self.start_time < other.start_time

    def get_modules(self):
        return self._modules

    def overlaps(self, module):
        #stackoverflow 325933
        return max(self.start_time, module.start_time) < min(self.end_time,module.end_time)

    def span(self,headers):
        start = 0
        end = 0
        for i in range(len(headers)):
            if self.start_time == headers[i]:
                start = i
            elif self.end_time == headers[i]:
                end = i
        assert end-start > 0
        return end-start

class Timetable:
    def __init__(self, path):
        self.timetable = pyxl.load_workbook(paths[2], read_only = True, data_only = True).active
        self.days = ("Mon","Tue","Wed","Thu","Fri","Sat","Sun")
        self.bins = {day:[] for day in self.days}


    def generate_event_list(self,codes):
        eventlist = set()
        for row in self.timetable.iter_rows(min_row=2,values_only=True):
            module = str(row[1])
            if module and any(matches(x,codes) for x in module.split(',')):
                eventlist.add(row[0])
        return list(eventlist)

    def load_events(self,eventlist):
        headers = set()
        eventlist = sorted(eventlist)
        for row in self.timetable.iter_rows(min_row=2,values_only=True):
            if row[0] in eventlist:
                if not row[4] or not row[5] or not row[8]:
                    print("Warning: Missing date/time/room info for event id",row[0])
                    continue
                event = Event(row)
                self.bins[event.day].append(event)
                headers.update((event.start_time,event.end_time))
        self.headers = sorted(headers)
        for bin in self.bins.values():
            bin.sort()


    def create_timetable(self, eventlist, headerbg = '#C0C0C0', headerfont = '#000000', cellbg = '#00FFFF', cellfont = '#000000'):
        self.load_events(eventlist)
        doc, tag, text, line = Doc().ttl()
        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('head'):
                line('title','Time Table Test')
            with tag('body'):
                with tag('table', cellspacing=0, border=1):
                    doc.asis('<!-- START COLUMNS HEADERS-->')
                    with tag('tr'):
                        line('td','')
                        for header in self.headers[:-1]:#last header marks end
                            with tag('td', bgcolor=headerbg, colspan=1):
                                line('font', str(minute_to_time(header))[:5], color=headerfont)
                    doc.asis('<!-- END COLUMNS HEADERS-->')
                    doc.asis('<!--START ROW OUTPUT-->')
                    for day in self.days:
                        with tag('tr'):
                            with tag('td', bgcolor=headerbg, rowspan=1):
                                line('font',day,color=headerfont)
                            index = 0
                            for i in range(len(self.headers)-1):
                                if index != i:
                                    continue
                                header = self.headers[i]
                                events = [x for x in self.bins[day] if x.start_time == header]
                                if events:
                                    #TODO: Handle overlaps
                                    event = events[0]
                                    span = event.span(self.headers)
                                    with tag('td', bgcolor=cellbg, colspan=span, rowspan=1):
                                        with tag('table', bgcolor=cellbg, cellspacing=0, border=0, width='100%'):
                                            with tag('tr'):
                                                line('td',event.modules,align='left')
                                        with tag('table', bgcolor=cellbg, cellspacing=0, border=0, width='100%'):
                                            with tag('tr'):
                                                line('td',event.room,align='left')
                                        with tag('table', bgcolor=cellbg, cellspacing=0, border=0, width='100%'):
                                            with tag('tr'):
                                                line('td',str(event.weeks),align='left')
                                    index+=span
                                else:
                                    index+=1
                                    with tag('td'):
                                        doc.asis('&nbsp')







        return indent(doc.getvalue())

def matches(string, patterns):
    return any(string.startswith(pattern) for pattern in patterns)

if __name__ == "__main__":
    files = ["Room List.xlsx", "Roomequip.xlsx", "Timetable2018-19.xlsx","buildings.csv"]
    paths = [os.path.join("Data",x) for x in files]

    #buildings = load_buildings(paths[3])
    #rooms = load_rooms(paths[0], paths[1], buildings)

    #timetable = pyxl.load_workbook(paths[2]).active
    t = Timetable(paths[2])
    list = t.generate_event_list(["CS1"])

    out = t.create_timetable(list)
    with open ('timtable.html','w') as f:
        f.write(out)
    #get_info(paths[2])
