#!/usr/bin/env python

import sys
import time
import argparse
import urllib
import json

from common import db_write
from common import add_common_parser_args

DB_URI = "http://localhost:8086/write?db=inforad"


def get_jenkins_status(branch):
    url = ("https://ratchet.do.citrite.net/job/xenserver-specs/job/"
           "%s/api/json") % branch
    return json.load(urllib.urlopen(url))


def is_last_build_successful(status):
    return (status['lastSuccessfulBuild']['number'] ==
            status['lastCompletedBuild']['number'])


def is_last_build_stable(status):
    return (status['lastStableBuild']['number'] ==
            status['lastCompletedBuild']['number'])


def parse_args_or_exit(argv=None):
    parser = argparse.ArgumentParser(
        description='Get latest build and BVT status and add to dashboard DB')
    add_common_parser_args(parser)
    return parser.parse_args(argv)


def main():
    args = parse_args_or_exit(sys.argv[1:])
    status = get_jenkins_status('trunk%252Fring3')
    build_status = is_last_build_successful(status)
    bvt_status = is_last_build_stable(status)
    if args.dry_run:
        print "Build status: %s" % ("PASSED" if build_status else "FAILED")
        print "BVT status: %s" % ("PASSED" if bvt_status else "FAILED")
        exit(0)
    timestamp = int(time.time()) * 10**9
    db_write(DB_URI, "build_status", (1 if build_status else 0), timestamp)
    db_write(DB_URI, "bvt_status", (1 if bvt_status else 0), timestamp)

if __name__ == "__main__":
    main()
