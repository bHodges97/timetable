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
        self._init_weeks(row[7]) # weeks is set object for each week number
        self.room = row[8]
        self.string_data = row[9]
        self.room_pool = row[10]
        self.notes = row[11]
        self.details = row[12]

        self.length_time = str_to_minute(self.length)
        self.start_time = time_to_minute(self.time)
        self.end_time = self.start_time + self.length_time

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

    def overlaps(self, event): #stackoverflow 325933
        return max(self.start_time, event.start_time) < min(self.end_time, event.end_time)

    def conflicts(self, event):
        if self.overlaps(event):
            #different room and group
            return self.room != event.room and not self.groups.isdisjoint(event.groups)
        return False

    def col_span(self,headers):
        for i,header in enumerate(headers):
            if self.start_time == header:
                self.start = i
            elif self.end_time == header:
                self.end = i
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
        date = sorted(self.date)
        dates = ""
        if date:
            dates+=str(date[0])
            for date in date[1:]:
                dates+=","+str(date)
        return dates

    def modules_str(self):
        return ",".join(self.modules) if self.modules else ""

    def groups_str(self):
        return ",".join(self.groups) if self.groups else ""

    def __str__(self):
        attr = map(str,[self.modules_str(),self.type,self.groups_str(),self.room,self.day,self.start,self.length,self.weeks_str()])
        return ",".join(attr)

    def __lt__(self, other):
        return self.start_time < other.start_time

