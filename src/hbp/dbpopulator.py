#!/usr/bin/env python3

## -------------------------------------------------------------------------- ##
## HBP Downloader
## Using statcast data, builds a skeet and downloads the video. Also updates
## the HBP database for the plotter script.
## -------------------------------------------------------------------------- ##


import argparse
import pprint
import sys
import time

# Import application modules
from .libhbp import constants as const
from .libhbp import func_database as dbmgr
from .libhbp import func_general as gen
from .libhbp import func_baseball as bb

from .libhbp import basic
from .libhbp.configurator import ConfigReader
from .libhbp.logger import PrintLogger

from datetime import datetime, timedelta
from typing import Optional


## -------------------------------------------------------------------------- ##
## SETUP
## -------------------------------------------------------------------------- ##

## Command line parsing
parser = argparse.ArgumentParser(
    description="Populates sqlite3 database with HBP events."
)
parser.add_argument(
    "-b",
    "--backward",
    action="store_true",
    default=None,
    help="Go backward in time instead of the default backward.",
)
parser.add_argument(
    "-s",
    "--start-date",
    type=gen.parse_date_string,
    default="2025-11-01",
    help="Start date to check for HBP events. Must be in '2025-11-01' format. Defaults to '%(default)s'.",
)
parser.add_argument(
    "-d",
    "--num-days",
    type=int,
    default=1,
    help="Number of days to check for HBP events. Defaults to '%(default)s'.",
)
parser.add_argument(
    "-n",
    "--nolog",
    action="store_true",
    default=None,
    help="Disable logging.",
)
parser.add_argument(
    "-t",
    "--test-mode",
    action="store_true",
    help="Enable test mode, which makes this script pretend to do things.",
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

args = parser.parse_args()

## Read and update configuration
config = ConfigReader(basic.verify_file_path(basic.sanitize_path(const.DEFAULT_CONFIG_INI_FILE)))

sleep_time = float(config.get("operations", "sleep_time"))

start_date = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
if args.start_date:
    start_date = args.start_date

num_days = 1
if args.num_days and num_days > 0:
    num_days = args.num_days

backward = False
if args.backward:
    backward = True

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
        config.get("logging", "downloader_prefix"),
    )


## -------------------------------------------------------------------------- ##
## MAIN ACTION
## -------------------------------------------------------------------------- ##

def main(start_date: Optional[str] = None) -> int:
    try:
        print()

        if verbose:
            print(config.get_all())
            print()

        print("="*80)
        print(f" ⚾ {config.get('app', 'name')} ⚾ ~~> 📈 DB Populator")
        print("="*80)
        start_time = time.time()

        total_hbp_events = 0
        for xday in range(num_days):
            print(f'⚾ [{xday+1}/{num_days}] Checking {start_date} for games...', end='')
            mlb_games = bb.get_mlb_games_for_date(start_date)
            print(f'found {len(mlb_games)} games that day. ⚾')
        
            ## "GAME" FOR LOOP
            ## Loops through all the games for the day.
            hbp_count = 0
            for i, game in enumerate(mlb_games):
                game_deets = bb.get_mlb_game_deets(game, double_verbose) 
                hbp_events = bb.get_mlb_hit_by_pitch_events_from_single_game(game, double_verbose)       
        
                if double_verbose:
                    print("@ --------- GAME DEETS --------- ")
                    pprint.pprint(game_deets)
                    print("@ --------- HBP EVENTS --------- ")
                    pprint.pprint(hbp_events)
                    print("@ ------------ END ------------- ")
                    print()
                ## "HBP EVENT" FOR LOOP
                ## Loops through all the HBP events.
                for j, event in enumerate(hbp_events):        
                    try:
                        dbinsert_result = dbmgr.insert_row(game_deets, event)
                        hbp_count = hbp_count + 1

                        if dbinsert_result:
                            print(f"  {hbp_count:02}. 👍 HBP {event['play_id']} added to database.")
                        else:
                            print(f"  {hbp_count:02}. 🦋 HBP {event['play_id']} is already in the database.", end='')
                            if dbmgr.has_been_downloaded(event['play_id']):
                                print(f" (dl)", end='')
                            if dbmgr.has_been_analyzed(event['play_id']):
                                print(f" (nz)", end='')
                            if dbmgr.has_been_skeeted(event['play_id']):
                                print(f" (sk)", end='')
                            print()                            
                    except KeyboardInterrupt:
                        dbmgr.remove_row(event['play_id'])
                time.sleep(sleep_time)
            print(f"💥 There were {hbp_count} total HBP events for this day. 💥")
            print()
            total_hbp_events = total_hbp_events + hbp_count

            if backward:
                start_date = gen.subtract_one_day_from_date(start_date)
            else:
                start_date = gen.add_one_day_to_date(start_date)
        
        print(f"⚾💥 Captured {total_hbp_events} during this run.")

        print()
        end_time = time.time()
        elapsed = end_time - start_time
        print("="*80)
        print(f'Completed in {elapsed:.2f} seconds')
        print("="*80)
        print()
        return 0

    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(start_date))
