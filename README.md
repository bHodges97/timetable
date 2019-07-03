# timetable maker
Creates a HTML timetable.

## Installation
```
pip install -r requirements.txt
```

## Usage
Generate list event_id from list of modules:
```
python3 getevents.py "spreadsheet path" module ... -o "output file"
```

Generate timetable from list of events:
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
