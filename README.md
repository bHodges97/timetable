# timetable maker
Creates HTML timetable.

## Installation
```
pip install -r requirements.txt
```

## Usage
Generate event_id list from list of modules. The given modules matches the start of the module codes in the spreasheet. For example, 'CS' would match all module codes beginnng with cs.
```
python3 getevents.py "spreadsheet path" module ... -o "output file"
```


Generate timetable from event_id list:
```
python3 createtable.py "spreadsheet path" "event_id path" -o "output.html"
```


## Issues

Missing room capacity for:
* L33-G11
* JJT-SLINGO
* LYLE-G72
* RUSS-R017
* FOXH-G04
* HBS-202
* HBS-G09
