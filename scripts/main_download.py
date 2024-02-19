import argparse
import transportanalysis.download as dd
from transportanalysis import loading


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--buses",
                        help="collect buses for number of minutes")
    parser.add_argument("-l", "--stoploc", action='store_true',
                        help="collect location of all the bus stops")
    parser.add_argument("-n", "--buslines", action='store_true',
                        help="collect lines going through every bus stop, required first doing -l")
    parser.add_argument("-s", "--schedule", action='store_true',
                        help="collect very schedule for every line for every busstop, required first doing -l and -n")

    args = parser.parse_args()

    if args.buses:
        dd.DataRetrieval.collect_bus_location(args.buses)
    if args.stoploc:
        dd.DataRetrieval.collect_busstops_location()
    if args.buslines:
        text = input("Are you sure? (it takes long time) [Y/N]: ")
        if text.strip() == "Y":
            dd.DataRetrieval.collect_lines_all()
    if args.schedule:
        text = input("Are you sure? (it takes a few hours) [Y/N]: ")
        if text.strip() == "Y":
            dd.DataRetrieval.collect_schedule_all()


if __name__ == "__main__":
    main()
