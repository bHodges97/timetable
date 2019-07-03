from timetable import Timetable
import argparse
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List event_id for modules')
    parser.add_argument('path', metavar='path',  help='File path to timetable xlsx spreadsheet.')
    parser.add_argument('modules', metavar='module', nargs='+', help='List of modules.')
    parser.add_argument('-o', metavar='output file', help='Output file location.')
    args = parser.parse_args()

    t = Timetable(args.path)
    events = t.generate_event_list(args.modules)
    if args.o:
        with open(args.o,'w') as f:
            for event in events:
                f.write(str(event)+'\n')
    else:
        for event in events:
            print(event)



