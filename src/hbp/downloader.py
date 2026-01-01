#!/usr/bin/env python3

## -------------------------------------------------------------------------- ##
## HBP Downloader
## Using statcast data, builds a skeet and downloads the video. Also updates
## the HBP database for the plotter script.
## -------------------------------------------------------------------------- ##


import argparse
import os
import pprint
import sys
import time

# Import application modules
from .libhbp import basic
from .libhbp import constants as const
from .libhbp import func_baseball as bb
from .libhbp import func_database as dbmgr
from .libhbp import func_general as gen
from .libhbp import func_skeet as sk
from .libhbp.configurator import ConfigReader
from .libhbp.logger import PrintLogger

from datetime import date, datetime, timedelta
from typing import Optional


## -------------------------------------------------------------------------- ##
## SETUP
## -------------------------------------------------------------------------- ##

## Command line parsing
parser = argparse.ArgumentParser(
    description="Finds HBP events, prepares skeets, and downloads videos."
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
    "--skip-video-dl",
    action="store_true",
    help="Skips video download for each HBP.",
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

backward = False
if args.backward:
    backward = True

start_date = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
if args.start_date:
    start_date = args.start_date

num_days = 1
if args.num_days and num_days > 0:
    num_days = args.num_days

skip_video_dl = False
if args.skip_video_dl:
    skip_video_dl = True

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

## Other stuff that we can't set on the command line
skeet_dir = config.get("paths", "skeet_dir")
video_dir = config.get("paths", "video_dir")


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
        print(f" ⚾ {config.get('app', 'name')} ⚾ ~~> 💽 Downloader")
        print("="*80)
        start_time = time.time()

        if start_date == date(2025, 11, 1):
            print(f"Given start date, {start_date}, is the default date.")
            start_date = dbmgr.get_latest_date_that_hasnt_been_downloaded()
            print(f"New starting date: {start_date}")
            print()

        total_hbp_events = 0
        for xday in range(num_days):
            print("--->")
            print(f'⚾ Checking {start_date} for games...', end='')
            mlb_games = bb.get_mlb_games_for_date(start_date)
            print(f'found {len(mlb_games)} games that day. ⚾')
            print()
        
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

                ## Nobody got hit during this game....
                if hbp_events is None or len(hbp_events) == 0:
                    skeet_filename = sk.write_desc_skeet_text(game_deets, [], skeet_dir, double_verbose)
                    if verbose:
                        print(f"{i + 1}. Skeet File: {skeet_filename}")
                    skeet_text = sk.read_skeet_text(skeet_filename)
                    print(f"{skeet_text}")
                    print()
                    continue
                
                ## "HBP EVENT" FOR LOOP
                ## Loops through all the HBP events.
                for j, event in enumerate(hbp_events):      
                    hbp_count = hbp_count + 1
                    
                    ## Check if event is already in database. If not, add it.
                    dbdata = dbmgr.get_hbp_play_data(event['play_id'])
                    if len(dbdata) == 0:
                        dbinsert_result = dbmgr.insert_row(game_deets, event)
                        if dbinsert_result:
                            print(f"👍 HBP {event['play_id']} added to database.")
                        else:
                            raise Exception("Something is definitely wrong with the database file.")

                    ## Generate skeet
                    skeet_filename = sk.write_desc_skeet_text(game_deets, event, skeet_dir, double_verbose)
                    if verbose:
                        print(f"{i + 1}. Skeet File: {skeet_filename}")
                    ## Print skeet to screen
                    skeet_text = sk.read_skeet_text(skeet_filename)
                    print(f"{skeet_text}")
                    
                    ## Finally, download the video.    
                    if event['play_id'] is None or event['play_id'] == '':
                        print(f"😢 Video unavailable.")
                    else:
                        ## download video
                        if test_mode:
                            print("Pretending to download video....")
                        elif skip_video_dl:
                            pass
                        else:
                            video_filename = gen.download_baseball_savant_play(game['gamePk'], event['play_id'], verbose)
                            print(f"VIDEO: {video_filename}")
                            
                            if os.path.exists(video_filename):
                                dbmgr.set_download_flag(event['play_id'])                         

                    print()
            print(f"💥 There were {hbp_count} total HBP events for this day. 💥")
            print("<---\n")
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
