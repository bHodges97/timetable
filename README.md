# Timetable
Creates HTML timetable.

## Installation
```
pip3 install -r requirements.txt
```

## Usage
Generate event_id list from list of modules. The given modules matches the start of the module codes in the spreasheet. For example, 'CS' would match all module codes beginnng with CS.
```
python3 getevents.py "spreadsheet path" module ... -o "output file"
```


Generate timetable from event_id list:
```
python3 createtable.py "spreadsheet path" "event_id path" -o "output.html"
```


## Issues
Notes:
- Room pool
- String data
- Weeks field contains dates, dates have inconsistent formating(dd/mm and mm/dd)

Room capacity is Empty:
 * PALMERFOYER
 * PALMERFOYER1

Equiment listed but room capacity missong:
* L33-G11
* JJT-SLINGO
* LYLE-G72
* RUSS-R017
* FOXH-G04
* HBS-202
* HBS-G09
