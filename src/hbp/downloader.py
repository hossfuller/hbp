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
from . import constants as const
from . import func_general as gen
from . import func_baseball as bb
from . import func_skeet as sk

import libhbp.basic as libhbp
from libhbp.configurator import ConfigReader
from libhbp.logger import PrintLogger

from datetime import datetime, timedelta
from pathlib import Path
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
    help="Force HBP seek to go backward in time instead of the default backward.",
)
parser.add_argument(
    "-d",
    "--date",
    type=gen.parse_date_string,
    default="2025-11-01",
    help="Date to check for HBP events. Must be in '2023-08-01' format. Defaults to yesterday\'s date (default: '%(default)s').",
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
parser.add_argument(
    "-a",
    "--autopilot",
    action="store_true",
    help="Go until a keyboard interrupt is caught.",
)
parser.add_argument(
    "--only-db-insert",
    action="store_true",
    help="Only updates the database for each HBP.",
)
parser.add_argument(
    "--skip-db-insert",
    action="store_true",
    help="Skips updating the database for each HBP.",
)
parser.add_argument(
    "--skip-video-dl",
    action="store_true",
    help="Skips video download for each HBP.",
)

args = parser.parse_args()

## Read and update configuration
config = ConfigReader(libhbp.verify_file_path(libhbp.sanitize_path(const.DEFAULT_CONFIG_INI_FILE)))

start_date = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
if args.date:
    start_date = args.date

backward = False
if args.backward:
    backward = True

autopilot = False
if args.autopilot:
    autopilot = True

only_db_insert = False
if args.only_db_insert:
    only_db_insert = True

skip_db_insert = False
if args.skip_db_insert:
    skip_db_insert = True

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
plot_dir  = config.get("paths", "plot_dir")
skeet_dir = config.get("paths", "skeet_dir")
video_dir = config.get("paths", "video_dir")

db_table     = config.get("database", "hbp_table")
db_file_path = Path(
    config.get("paths", "db_dir"), 
    config.get("database", "hbp_db_filename")
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
        print(f" {config.get('app', 'name')} ~~> 💽 Downloader")
        print("="*80)
        start_time = time.time()

        total_hbp_events = 0
        found_hbp_events = False
        while not found_hbp_events:
            print()
            print(f'** Checking {start_date} for games...', end='')
            mlb_games = bb.get_mlb_games_for_date(start_date)
            print(f'found {len(mlb_games)} games that day. **')
            if double_verbose:
                pprint.pprint(mlb_games)

            ## "GAME" FOR LOOP
            hbp_count = 0
            for index, game in enumerate(mlb_games):
                print()
                game_deets = bb.get_mlb_game_deets(game, double_verbose)

                hbp_events = bb.get_mlb_hit_by_pitch_events_from_single_game(game, double_verbose)
                if hbp_events is None or len(hbp_events) == 0:
                    if not only_db_insert:
                        skeet_filename = sk.write_desc_skeet_text(game_deets, [], skeet_dir, double_verbose)
                        if verbose:
                            print(f"{index + 1}. Skeet File: {skeet_filename}")
                        skeet_text = sk.read_skeet_text(skeet_filename)
                        print(f"{skeet_text}")
                        continue

                if double_verbose:
                    pprint.pprint(hbp_events)

                ## "HBP EVENT" FOR LOOP
                for jndex, event in enumerate(hbp_events):

                    ## Insert into the database first.
                    if not skip_db_insert:
                        try:
                            dbinsert_result = gen.safe_dbinsert(game_deets, event, db_file_path)
                            hbp_count = hbp_count + 1

                            if dbinsert_result:
                                print(f"    {hbp_count}. 👍 HBP {event['play_id']} added to database.")
                            else:
                                ## If it's already in the database, then check 
                                ## everything's already been skeeted. If so, move on.
                                print(f"    {hbp_count}. 🦋 HBP {event['play_id']} is already in the database", end='')
                                if gen.has_already_been_skeeted(event['play_id'], db_file_path):
                                    print(" and has already been skeeted", end='')
                                print(".\n")
                                continue
                        except KeyboardInterrupt:
                            gen.remove_row(event['play_id'], db_file_path)

                    ## Looks like someone just wants to populate the database.
                    if only_db_insert:
                        continue

                    ## Generate skeet
                    skeet_filename = sk.write_desc_skeet_text(game_deets, event, skeet_dir, double_verbose)
                    if verbose:
                        print(f"{index + 1}. Skeet File: {skeet_filename}")
                    ## Print skeet to screen
                    skeet_text = sk.read_skeet_text(skeet_filename)
                    print(f"{skeet_text}")

                    ## Finally, download the video.
                    if event['play_id'] is None or event['play_id'] == '':
                        print(f"😢 Video unavailable.")
                        ## if there's no video, there's no video.
                        gen.set_video_as_downloaded(event['play_id'], db_file_path)
                    else:
                        ## download video
                        if test_mode:
                            print("Pretending to download video....")
                        elif skip_video_dl:
                            pass
                        else:
                            video_filename = gen.download_baseball_savant_play(game['gamePk'], event['play_id'], video_dir, verbose)
                            print(f"VIDEO: {video_filename}")
                            if os.path.exists(video_filename):
                                gen.set_video_as_downloaded(event['play_id'], db_file_path)

                    print()
            
            print(f"    ⚾💥 There were {hbp_count} total HBP events for this day.")
            total_hbp_events = total_hbp_events + hbp_count

            if autopilot:
                if backward:
                    start_date = gen.subtract_one_day_from_date(start_date)
                else:
                    start_date = gen.add_one_day_to_date(start_date)
            else:
                found_hbp_events = True

        print()
        print(f"** Captured {total_hbp_events} during this run.")

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
    sys.exit(main(start_date))
