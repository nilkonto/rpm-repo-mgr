# coding=utf-8
__author__ = 'Wojciech Urbański'

import os
import sys
import glob
import logging
import shutil
from subprocess import call

import argparse
from pyrpm.rpm import RPM
from pyrpm import rpmdefs


def configure_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="path to get .rpm's from")
    parser.add_argument("destination", help="path to put .rpm's to")
    parser.add_argument("-r", "--recursive", help="copy files from source recursively", action='store_true')
    parser.add_argument("-p", "--purge", help="purge (do not backup) old packages", action='store_true')
    parser.add_argument("-x", "--execute", help="post-execute an app on destination dir (default: /usr/bin/createrepo)",
                        default='/usr/bin/createrepo')
    parser.add_argument("-v", "--verbose", action='store_true', help="print verbose output")
    args = parser.parse_args()
    return args


def get_metadata(path):
    if os.path.isfile(path):
        rpmfile = RPM(file(os.path.abspath(path)))
        metadata = {rpmfile.name():
                        {'version': rpmfile[rpmdefs.RPMTAG_VERSION],
                         'path': os.path.abspath(path),
                         'arch': rpmfile[rpmdefs.RPMTAG_ARCH]}
        }
        return metadata
    else:
        return None


def search_source(path, recursive):
    index = {}
    if os.path.isfile(os.path.abspath(path)):
        index.update(get_metadata(os.path.abspath(path)))
    elif os.path.isdir(os.path.abspath(path)):
        if recursive:
            for root, _, files in os.walk(os.path.abspath(path)):
                for package in files:
                    if package.endswith(".rpm"):
                        index.update(get_metadata(os.path.join(root, package)))
        else:
            for package in glob.glob(os.path.join(os.path.abspath(path), '*.rpm')):
                index.update(get_metadata(package))
    else:
        return None
    return index


def search_dest(destination):
    index = {}
    path = os.path.abspath(destination)
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for package in files:
                if package.endswith(".rpm"):
                    index.update(get_metadata(os.path.join(root, package)))
        return index
    else:
        return None


def update_package(new, old, destination, purge):
    if os.path.isfile(new['path']) and os.path.isfile(old['path']):
        if purge:
            os.remove(old['path'])
        else:
            os.rename(old['path'], old['path'] + '.bak')
        destpath = os.path.join(os.path.abspath(destination), new['arch'], os.path.basename(new['path']))
        try:
            os.makedirs(os.path.dirname(destpath))
        except OSError:
            if not os.path.isdir(os.path.dirname(destpath)):
                raise

        shutil.copyfile(new['path'],
                        destpath)
        return 0
    else:
        return None


def main():
    logging.basicConfig(format='%(asctime)s %(message)s')
    args = configure_parser()
    if args:
        source_index = search_source(args.source, args.recursive)
        dest_index = search_dest(args.destination)

        if source_index:
            packagesToUpdate = list(set(source_index.keys()) & set(dest_index.keys()))

            if args.verbose:
                print "Copying packages to repo"
                print "From: {0}".format(args.source)
                print "To: {0}".format(args.destination)
                print "Found source packages: {0}".format(source_index.keys())
                print "Found current packages: {0}".format(dest_index.keys())
                print packagesToUpdate
            # TODO: Edit to include all packages from souce, not only the repeated ones
            for package in packagesToUpdate:
                if not update_package(source_index[package], dest_index[package], args.destination, args.purge):
                    return 4
            if args.execute and call('{0} {1}'.format(args.execute, args.destination), shell=True):
                return 5
        else:
            print "No .rpm's found in directory {0}".format(args.source)
            return 2
    else:
        print "Unspecified error"
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())