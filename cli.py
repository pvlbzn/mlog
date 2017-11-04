import os
import sys
import argparse

from utils import Reader, Timeframe


def set_parser():
    parser = argparse.ArgumentParser(
        description='Automatic time tracker client side command line interface'
    )
    parser.add_argument(
        '-p',
        '--print',
        action='store_true',
        help='calculate and print today\'s usage')
    parser.add_argument(
        '-pt',
        '--print_today',
        action='store_true',
        help='calculate and print today\'s usage')
    parser.add_argument(
        '-py',
        '--print_yesterday',
        action='store_true',
        help='calculate and print yesterday\'s usage')
    parser.add_argument(
        '-pw',
        '--print_week',
        action='store_true',
        help='calculate and print week\'s usage')
    parser.add_argument(
        '-pm',
        '--print_month',
        action='store_true',
        help='calculate and print month\'s usage')
    parser.add_argument(
        '-t',
        '--threshold',
        action='store',
        dest='threshold',
        type=int,
        help='set threshold value in seconds')

    return parser


def main():
    parser = set_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    r = Reader()
    t = 5 if args.threshold == None else args.threshold

    if args.print or args.print_today:
        print('Data range: today')
        Timeframe(r.today()).print(threshold=t)
        return

    if args.print_yesterday:
        print('Data range: yesterday')
        Timeframe(r.yesterday()).print(threshold=t)
        return

    if args.print_week:
        print('Data range: last week')
        Timeframe(r.last_weeks(1)).print(threshold=t)

    if args.print_month:
        print('Data range: last month')
        Timeframe(r.last_weeks(4)).print(threshold=t)


if __name__ == '__main__':
    main()
