from timetable import Timetable
import argparse
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create html time table from event list')
    parser.add_argument('path1', metavar='timetable path',  help='xlsx timetable file path')
    parser.add_argument('path2', metavar='event_id path',  help='event_id list file path ')
    parser.add_argument('-o', metavar='output file', help='Output file location.')
    args = parser.parse_args()

    t = Timetable(args.path1)
    with open(args.path2,'r') as f:
        events = f.read().splitlines()
        out = t.create_timetable(events)

        if args.o:
            with open(args.o,'w') as f1:
                f1.write(out)
        else:
            print(out)



