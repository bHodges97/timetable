import os
import numpy as np
import openpyxl as pyxl
from building import *
from timeutils import *
from yattag import Doc,indent

class TimeSlot:
    def __init__(self,event):
        self.events = [event]

    def add(self,event):
        self.events.append(event)

    def sort(self):
        if self.events[0]:
            self.events.sort(key = lambda x: 1000 if x.date else min(x.weeks))

    def matches(self, event):
        if self.events[0]:
            return self.events[0].same_except_room(event)

class Event:
    def __init__(self,row):
        self.id = row[0]
        self.modules = set(str(row[1]).split(','))
        self.type = row[2]
        if row[3]:
            self.group = set(str(row[3]).split(','))
        else:
            self.group = set()
        self.day = row[4]
        self.time = row[5]
        self.length = row[6]
        self._init_weeks(row[7]) # weeks is set object for each week number
        self.room = row[8]
        self.string_data = row[9]
        self.room_pool = row[10]
        self.notes = row[11]
        self.details = row[12]

        self.start_time = time_to_minute(self.time)
        self.end_time = self.start_time + str_to_minute(self.length)

    def __lt__(self, other):
        return self.start_time < other.start_time

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

    def can_merge_with(self, event):
        if event:
            return self.same_except_room(event) and self.room == event.room

    def same_except_room(self, event):
        return self.start_time == event.start_time and self.end_time == event.end_time and self.modules == event.modules and self.group == event.group and self.type == event.type and self.day == event.day

    def _init_weeks(self, data):
        self.weeks = set()
        self.date = set()
        if isinstance(data,datetime):
            self.date.add(str(data.date()))#strftime("%b-%d")
            return

        weeks_strs = str(data).split(",")
        for weeks in weeks_strs:
            terms = list(map(int,weeks.split("-")))
            if len(terms) == 1:
                self.weeks.add(terms[0])
            else:
                self.weeks.update(set(range(terms[0],terms[1]+1)))

    def merge_weeks(self,event):
        self.weeks.update(event.weeks)
        self.date.update(event.date)

    def weeks_str(self):
        out = ""
        weeks = sorted(self.weeks)
        if self.weeks:
            last = weeks[0]
            out = str(last)
            if len(self.weeks) > 1:
                weeks.append(0)#fixes tail
                for i in range(1,len(weeks)):
                    if weeks[i] != weeks[i-1]+1:
                        if last != weeks[i-1]:
                            out+= "-" + str(weeks[i-1])
                        out+= "," + str(weeks[i])
                        last=weeks[i]
                out = out[:-2]
        dates = self.date_str()
        return out + " " + dates

    def date_str(self):
        date = sorted(self.date)
        dates = ""
        if date:
            dates+=str(date[0])
            for date in date[1:]:
                dates+=","+str(date)
        return dates

    def modules_str(self):
        if self.modules:
            return ",".join(self.modules)
        else:
            return ""

    def groups_str(self):
        if self.group:
            return ",".join(self.group)
        else:
            return ""

class Timetable:
    def __init__(self, path):
        self.timetable = pyxl.load_workbook(path, read_only = True, data_only = True).active
        self.days = {day:[] for day in ("Mon","Tue","Wed","Thu","Fri","Sat","Sun")}
        self.events = []

    def generate_event_list(self,codes):
        eventlist = set()
        for row in self.timetable.iter_rows(min_row=2,values_only=True):
            module = str(row[1])
            if module and any(Timetable.matches(x,codes) for x in module.split(',')):
                eventlist.add(row[0])
        return list(eventlist)

    def load_events(self,eventlist):
        eventlist = sorted(eventlist)
        #load events from excel
        for row in self.timetable.iter_rows(min_row=2,values_only=True):
            if row[0] in eventlist:
                if not row[4] or not row[5] or not row[8]:
                    print("Warning: Missing date/time/room info for event id",row[0])
                    continue
                event = Event(row)
                for e in self.days[row[4]]:
                    if event.can_merge_with(e):
                        e.weeks.update(event.weeks)
                        event = None
                        break
                if event:
                    self.events.append(event)
                    self.days[event.day].append(event)
        for row in self.days.values():
            row.sort()

    def create_timetable(self):
        headers = set()
        for event in self.events:
            headers.update((event.start_time,event.end_time))
        headers = sorted(headers)

        self.rows = []
        for day,row in self.days.items():
            row.sort()
            cell_list = [[None] * (len(headers) - 1)]
            for event in row:
                event.span(headers)
                slotted = False
                i = 0
                while not slotted:
                    cells = cell_list[i]
                    #slot into time table if there is space
                    if cells[event.start] == None:
                        cells[event.start]= TimeSlot(event)
                        for i in range(event.start+1,event.end):
                            cells[i] = TimeSlot(None)
                        slotted = True
                    #if different type/group add to info
                    elif cells[event.start].matches(event):
                        cells[event.start].add(event)
                        slotted = True
                    else:#if in conflict add a new row
                        i+=1
                        if len(cell_list) == i:
                            cell_list.append([None] * (len(headers) -1))

            for cells in cell_list:
                [c.sort() for c in cells if c]
                self.rows.append((day,cells))
        self.headers = headers

    def list_modules(self):
        modules = set()
        for row in self.timetable.iter_rows(min_row=2,values_only=True):
            if row[1]:
                m = str(row[1]).split(",")
                modules.update(m)
        modules = sorted(modules)
        return modules

    def render_html(self, headerbg = '#C0C0C0', headerfont = '#000000', cellbg = '#00FFFF', cellfont = '#000000'):
        self.create_timetable()
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

                    for day,row in self.rows:
                        doc.asis('<!--START ROW '+day+'-->')
                        with tag('tr'):
                            with tag('td', bgcolor=headerbg, rowspan=1):
                                line('font',day,color=headerfont)
                            for cell in row:
                                if cell:
                                    event = cell.events[0]
                                    if not event:
                                        continue
                                    with tag('td', bgcolor=cellbg, colspan=event.span, rowspan=1):
                                        text = event.modules_str() + " " + event.type
                                        text += " " + event.groups_str()
                                        Timetable.create_table(text,tag,line,cellbg)
                                        for e in cell.events:
                                            Timetable.create_table(e.room,tag,line,cellbg)
                                            Timetable.create_table(e.weeks_str(),tag,line,cellbg)
                                else:#empty cell
                                    with tag('td'):
                                        doc.asis('&nbsp')
                        doc.asis('<!--END ROW '+day+'-->')


        return indent(doc.getvalue())

    def create_table(text,tag,line,cellbg):
        with tag('table', bgcolor=cellbg, cellspacing=0, border=0, width='100%'):
            with tag('tr'):
                line('td', text, align='left')

    def some_metrics(self, buildinglist):
        groups = dict()

        for event in self.events:
            for module in event.modules:
                if not module in groups:
                    groups[module] = set()
                if event.group:
                    for module in event.modules:
                        groups[module].update(event.group)

        print(groups.values())
        for i in self.days["Mon"]:
            print(i.start_time)
        #get all module codes and group combos


    def matches(string, patterns):
        return any(string.startswith(pattern) for pattern in patterns)

if __name__ == "__main__":
    files = ["Room List.xlsx", "Roomequip.xlsx", "Timetable2018-19.xlsx","buildings.csv"]
    paths = [os.path.join("Data",x) for x in files]

    #buildings = load_buildings(paths[3])
    #rooms = load_rooms(paths[0], paths[1], buildings)

    #timetable = pyxl.load_workbook(paths[2]).active
    t = Timetable(paths[2])
    eventlist = t.generate_event_list(["CS1"])
    t.load_events(eventlist)

    out = t.render_html()
    with open ('timetable.html','w') as f:
        f.write(out)
    #get_info(paths[2])
