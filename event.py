from timeutils import *

class Event:
    def __init__(self,row):
        self.id = row[0]
        self.modules = set(str(row[1]).split(','))
        self.type = row[2]
        self.groups = set(str(row[3]).split(',')) if row[3] else set()
        self.day = row[4]
        self.time = row[5]
        self.length = row[6]
        self._init_weeks(row[7]) # weeks is stored as set of all week numbers
        self.room = row[8]
        self.string_data = row[9]
        self.room_pool = row[10]
        self.notes = row[11]
        self.details = row[12]

        self.length_time = str_to_minute(self.length)
        self.start_time = time_to_minute(self.time)
        self.end_time = self.start_time + self.length_time

    def _init_weeks(self, data):
        self.date = set()
        self.weeks = set()
        if isinstance(data,datetime):
            self.date.add(str(data.date()))#strftime("%b-%d")
        else:
            self.weeks = range_to_set(str(data))

    def overlaps(self, event): #stackoverflow 325933
        return max(self.start_time, event.start_time) < min(self.end_time, event.end_time)

    def conflicts(self, event):
        if self.overlaps(event):
            #different room and group
            return self.room != event.room and not self.groups.isdisjoint(event.groups)
        return False

    def col_span(self,headers):
        self.start = headers.index(self.start_time)
        self.end = headers.index(self.end_time)
        self.span = self.end-self.start
        return self.span

    def can_merge_with(self, event):
        if event:
            return self.same_except_room(event) and self.room == event.room

    def same_except_room(self, event):
        return self.start_time == event.start_time and self.end_time == event.end_time \
                and self.modules == event.modules and self.groups == event.groups \
                and self.type == event.type and self.day == event.day

    def merge_weeks(self,event):
        self.weeks.update(event.weeks)
        self.date.update(event.date)

    def weeks_str(self):
        out = set_to_range(self.weeks)
        dates = self.date_str()
        return out + " " + dates

    def date_str(self):
        return ",".join(sorted(self.date)) if self.date else ""

    def modules_str(self):
        return ",".join(self.modules) if self.modules else ""

    def groups_str(self):
        return ",".join(self.groups) if self.groups else ""

    def __str__(self):
        attr = map(str,[self.modules_str(),self.type,self.groups_str(),self.room,self.day,self.start,self.length,self.weeks_str()])
        return ",".join(attr)

    def __lt__(self, other):
        return self.start_time < other.start_time

