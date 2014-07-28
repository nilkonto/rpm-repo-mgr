# coding=utf-8
__author__ = 'Wojciech Urbański'

import sys
import argparse


def configure_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="path to get .rpm's from")
    parser.add_argument("destination", help="path to put .rpm's to")
    parser.add_argument("-r", "--recursive", help="copy files from source recursively", action='store_true')
    parser.add_argument("-b", "--backup", help="backup old packages", action='store_true')
    args = parser.parse_args()
    return args


def main():
    args = configure_parser()
    print args.echo
    return 0


if __name__ == "__main__":
    sys.exit(main())