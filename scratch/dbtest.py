#!/usr/bin/env python3

## -------------------------------------------------------------------------- ##
## @TODO Section!
## -------------------------------------------------------------------------- ##


import argparse
import pprint
import sys
import time
import uuid

# Import application modules
from . import constants as const
from . import func_general as gen
from . import func_baseball as bb
from . import func_skeet as sk

import libhbp.basic
from libhbp.configurator import ConfigReader
from libhbp.logger import PrintLogger
from libhbp.sqlitemgr import SQLiteManager

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


## -------------------------------------------------------------------------- ##
## SETUP
## -------------------------------------------------------------------------- ##

## Command line parsing
parser = argparse.ArgumentParser(
    description="DB Test."
)
parser.add_argument(
    "-c",
    "--config",
    type=libhbp.basic.verify_file_path,
    default="config/settings.ini",
    help="Override default config with custom settings file (default: '%(default)s').",
)
parser.add_argument(
    "-n",
    "--nolog",
    action="store_true",
    default=None,
    help="Disable logging.",
)
parser.add_argument(
    "-p",
    "--plot-dir",
    type=libhbp.basic.verify_directory_path,
    default='plots',
    help="Directory storing plots.",
)
parser.add_argument(
    "-s",
    "--skeet-dir",
    type=libhbp.basic.verify_directory_path,
    default='skeets',
    help="Directory storing skeet text.",
)
parser.add_argument(
    "-t",
    "--test-mode",
    action="store_true",
    help="Enable test mode, which doesn't assume directory and file names are in the JDOC format.",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    default=None,
    help="Enables verbose output.",
)
parser.add_argument(
    "-vv",
    "--double-verbose",
    action="store_true",
    default=None,
    help="Enables really verbose output.",
)
parser.add_argument(
    "-z",
    "--video-dir",
    type=libhbp.basic.verify_directory_path,
    default='videos',
    help="Directory storing video files.",
)

args = parser.parse_args()

## Read and update configuration
config = ConfigReader(args.config)

plot_dir = config.get("paths", "plot_dir")
if args.plot_dir:
    config.set("paths", "plot_dir", args.plot_dir)
    plot_dir = args.plot_dir

skeet_dir = config.get("paths", "skeet_dir")
if args.skeet_dir:
    config.set("paths", "skeet_dir", args.skeet_dir)
    skeet_dir = args.skeet_dir

video_dir = config.get("paths", "video_dir")
if args.video_dir:
    config.set("paths", "video_dir", args.video_dir)
    video_dir = args.video_dir

test_mode = bool(int(config.get("operations", "test_mode")))
if args.test_mode:
    config.set("operations", "test_mode", "1")
    test_mode = True

verbose = bool(int(config.get("operations", "verbose_output")))
if args.verbose:
    config.set("operations", "verbose_output", "1")
    verbose = True

double_verbose = bool(int(config.get("operations", "double_verbose")))
if args.double_verbose:
    config.set("operations", "verbose_output", "1")
    config.set("operations", "double_verbose", "1")
    verbose        = True
    double_verbose = True

## Set up logging
if not args.nolog:
    sys.stdout = PrintLogger(
        config.get("paths", "log_dir"),
        config.get("logging", "plotter_prefix"),
    )


## -------------------------------------------------------------------------- ##
## MAIN ACTION
## -------------------------------------------------------------------------- ##

def main() -> int:
    try:
        print()

        if verbose:
            print(config.get_all())
            print()

        print("="*80)
        print(f" {config.get('app', 'name')} ~~> 📊 DB Test")
        print("="*80)
        start_time = time.time()

        db_dir      = config.get("paths", "db_dir")
        db_filename = config.get("database", "hbp_db_filename")
        db_table    = config.get("database", "hbp_table")
        db_file_path = Path(db_dir, db_filename)
        print(f"Writing to {db_table} to file '{db_file_path}'.")

        with SQLiteManager(db_file_path) as db: 
            db.insert_hbpdata(str(uuid.uuid4()), 111111, 222222, 333333, 86.7, 3.14, 6.28)
            db.insert_hbpdata(str(uuid.uuid4()), 444444, 555555, 666666, 92.1, 14.5, 9.01)
            db.insert_hbpdata(str(uuid.uuid4()), 777777, 888888, 999999, 95.5, 7.77, 19.77)

            all_data = db.read_hbpdata_all()
            print("All data:")
            pprint.pprint(all_data)
            print()

            select_data = db.get_hbpdata_data(
                f"SELECT * FROM {db_table} WHERE game_pk = ?",
                [444444]
            )
            print("Just some of the data:")
            pprint.pprint(select_data)


        print()
        end_time = time.time()
        elapsed = end_time - start_time
        print("="*80)
        print(f'Completed in {elapsed:.2f} seconds', file=sys.stderr)
        print("="*80)
        print()
        return 0

    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
