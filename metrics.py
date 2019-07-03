from timetable import Timetable

def list_modules(timetable):
    modules = set()
    for row in timetable.iter_rows(min_row=2,values_only=True):
        if row[1]:
            m = str(row[1]).split(",")
            modules.update(m)
    modules = sorted(modules)
    return modules

if __name__ == "__main__":
    timetable = Timetable('Data/Timetable2018-19.xlsx').timetable
    print(list_modules(timetable))


