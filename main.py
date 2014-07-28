# coding=utf-8
__author__ = 'Wojciech Urbański'

import os
import sys
import argparse
from pyrpm.rpm import RPM
from pyrpm import rpmdefs
import glob
import logging

def configure_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="path to get .rpm's from")
    parser.add_argument("destination", help="path to put .rpm's to")
    parser.add_argument("-r", "--recursive", help="copy files from source recursively", action='store_true')
    parser.add_argument("-p", "--purge", help="purge (do not backup) old packages", action='store_false')
    parser.add_argument("-x", "--execute", help="post-execute an app on destination dir (default: /usr/bin/createrepo)",
                        default='/usr/bin/createrepo')
    args = parser.parse_args()
    return args


def search_source(path, recursive):
    source_list = []
    if os.path.isfile(path):
        source_list.append(os.path.abspath(path))
    elif os.path.isdir(path):
        if recursive:
            temp_list = []
            for root, _, files in os.walk(os.path.abspath(path)):
                for package in files:
                    if package.endswith(".rpm"):
                        temp_list.append(os.path.join(root, package))
            source_list = temp_list
        else:
            source_list = glob.glob(os.path.join(os.path.abspath(path), '*.rpm'))
    else:
        return None
    return source_list


def main():
    logging.basicConfig(format='%(asctime)s %(message)s')
    args = configure_parser()
    if args is not None:
        package_list = search_source(args.source, args.recursive)
        if package_list is not None:
            print "Copying from {0} to {1}".format(args.source, args.destination)
            print package_list
        else:
            logging.error("No .rpm's found in directory {0}".format(args.source))
            return 2
    else:
        logging.error("Unknown error")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())