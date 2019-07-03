import os
import numpy as np
import openpyxl as pyxl
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
        self.weeks = str(row[7])
        self.room = row[8]
        self.string_data = row[9]
        self.room_pool = row[10]
        self.notes = row[11]
        self.details = row[12]

        self.start_time = time_to_minute(self.time)
        self.end_time = self.start_time + str_to_minute(self.length)
        self._modules = set(self.modules.split(','))
        self.info = []

    def __lt__(self, other):
        return self.start_time < other.start_time

    def get_modules(self):
        return self._modules

    def overlaps(self, event):
        #stackoverflow 325933
        return max(self.start_time, event.start_time) < min(self.end_time, event.end_time)

    def span(self,headers):
        for i in range(len(headers)):
            if self.start_time == headers[i]:
                self.start = i
            elif self.end_time == headers[i]:
                self.end = i
        self.span = self.end-self.start
        return self.span

    def same_time_module_and_room(self, event):
        return self.same_time_module_as(event) and self.room == event.room

    def same_time_module_as(self, event):
        return self.start_time == event.start_time and self.end_time == event.end_time and self._modules == event._modules and self.group == event.group

    def merge_weeks(self,event):
        self._modules.update(event._modules)
        self.module = ",".join(self._modules)
        self.weeks += "," + event.weeks

    def merge_rooms(self,event):
        for combo in self.info:
            if combo[0] == event.room:
                combo[1] += "," + event.weeks
                return

        self.info.append([event.room,event.weeks])

    def sort_contents(self):
        self.info.append([self.room,self.weeks])
        for combo in self.info:
            combo[1] = Event.sort_weeks(combo[1])
        self.info.sort(key = lambda x:int(x[1].split(",")[0].split("-")[0]))

    def sort_weeks(weeks):
        terms = weeks.split(",")
        terms.sort(key=lambda x:int(x.split('-')[0]))
        return ",".join(terms)


class Timetable:
    def __init__(self, path):
        self.timetable = pyxl.load_workbook(path, read_only = True, data_only = True).active
        self.days = ("Mon","Tue","Wed","Thu","Fri","Sat","Sun")


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
        bins = {day:[] for day in self.days}

        for row in self.timetable.iter_rows(min_row=2,values_only=True):
            if row[0] in eventlist:
                if not row[4] or not row[5] or not row[8]:
                    print("Warning: Missing date/time/room info for event id",row[0])
                    continue
                event = Event(row)
                bins[event.day].append(event)
                headers.update((event.start_time,event.end_time))

        headers = sorted(headers)
        self.bins = []
        for day in self.days:
            bins[day].sort()
            cell_list = [[None] * (len(headers) - 1)]
            for event in bins[day]:
                event.span(headers)
                slotted = False
                i = 0
                while not slotted:
                    cells = cell_list[i]
                    #slot into time table if time slot empty
                    if cells[event.start] == None:
                        for i in range(event.start,event.end):
                            cells[i] = event
                        slotted = True
                    #if in same room, mege
                    elif cells[event.start].same_time_module_and_room(event):
                        cells[event.start].merge_weeks(event)
                        slotted = True
                    elif cells[event.start].same_time_module_as(event):
                        cells[event.start].merge_rooms(event)
                        slotted = True
                    else:
                        i+=1
                        if len(cell_list) == i:
                            cell_list.append([None] * (len(headers) -1))

            for cells in cell_list:
                self.bins.append((day,cells))
        for day,cells in self.bins:
            for event in set(cells):
                if event:
                    event.sort_contents()

        self.headers = headers



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
                    for day,cells in self.bins:
                        with tag('tr'):
                            with tag('td', bgcolor=headerbg, rowspan=1):
                                line('font',day,color=headerfont)
                            skip = 0
                            for cell in cells:
                                if skip:
                                    skip-=1
                                    continue
                                if cell:
                                    with tag('td', bgcolor=cellbg, colspan=cell.span, rowspan=1):
                                        text = cell.modules + " " + cell.type
                                        if cell.group:
                                            text+=" " + str(cell.group)
                                        Timetable.create_table(text,tag,line,cellbg)
                                        for room,week in cell.info:
                                            Timetable.create_table(room,tag,line,cellbg)
                                            Timetable.create_table(week,tag,line,cellbg)
                                    skip = cell.span-1
                                else:
                                    with tag('td'):
                                        doc.asis('&nbsp')

                    doc.asis('<!--END ROW OUTPUT-->')

        return indent(doc.getvalue())

    def create_table(text,tag,line,cellbg):
        with tag('table', bgcolor=cellbg, cellspacing=0, border=0, width='100%'):
            with tag('tr'):
                line('td', text, align='left')


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
    with open ('timetable.html','w') as f:
        f.write(out)
    #get_info(paths[2])
