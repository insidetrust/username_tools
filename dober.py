import itertools
import datetime
from dateutil.relativedelta import relativedelta
import logging
import argparse


def roundrobin(*iterables):
    # roundrobin('ABC', 'D', 'EF') --> A D E B F C
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = itertools.cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = itertools.cycle(itertools.islice(nexts, pending))


class DOBer():
    def __init__(self, average_age, minimum_age, maximum_age, python_format):
        self.average_age = average_age
        self.maximum_age = maximum_age
        self.minimum_age = minimum_age
        self.format = python_format
        self.combined = ()

    def generate(self):

        base = datetime.datetime.now() - relativedelta(years=self.average_age)

        date_list1 = [base - datetime.timedelta(days=x) for x in range(1, (self.maximum_age - self.average_age) * 365)]
        date_list2 = [base + datetime.timedelta(days=x) for x in range(0, (self.average_age - self.minimum_age) * 365)]

        self.combined = roundrobin(date_list1, date_list2)

    def write_files(self, filename):
        myfile = open(filename, 'w')

        for item in self.combined:
            myfile.write("%s\n" % item.strftime(self.format))


if __name__ == "__main__":

    title = '''

    ,------.   ,-----. ,-----.
    |  .-.  \ '  .-.  '|  |) /_  ,---. ,--.--.
    |  |  \  :|  | |  ||  .-.  \| .-. :|  .--'
    |  '--'  /'  '-'  '|  '--' /\   --.|  |
    `-------'  `-----' `------'  `----'`--'

                 (   )   (
                 @   @   @
                _i___i___i_
               (___________)
               |==[HAPPY]==|
               (__[B'DAY]__)
               <-----+----->
                    -|-
                   / | \\
                __.  |  .__
              ---------------

    DOBer, a tool for generating date-of-birth lists in likelihood order.
    May be quite efficient, assuming that an applications' user-age follows
    a normal distribution, some kind of bell-curve, or similar distribution.

    Ben Williams, NCC Group 2016


Date-of-birth can be generated in various formats:

Example: python dober.py --max 50 --min 12 --average 25 --format "%d%m%y"
291176

Example: python dober.py --max 26 --min 21 --average 23 --format "%b-%d-%Y" -o test.txt
Nov-29-1993
'''

    print(title)

    logging.basicConfig(format="[%(levelname)s]-%(threadName)s: %(message)s", level=logging.DEBUG)
    parser = argparse.ArgumentParser()

    parser.add_argument("--format", help="Format string to use for date format",
                        default='%d-%m-%y')

    parser.add_argument("-o", "--output", help="File to output",
                        default='output.txt')

    parser.add_argument("--max", help="Maximum users age.", type=int,
                        default=65)

    parser.add_argument("--min", help="Minimum users age.", type=int,
                        default=18)

    parser.add_argument("--average", help="Average users age.", type=int,
                        default=40)


    args = parser.parse_args()

    list_object = DOBer(args.average, args.min, args.max, args.format)
    list_object.generate()
    list_object.write_files(args.output)

    print("File '%s' generated" % args.output)
    print("\nFinished!")


