#!/usr/bin/env python3

## -------------------------------------------------------------------------- ##
## @TODO Section!
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

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


## -------------------------------------------------------------------------- ##
## SETUP
## -------------------------------------------------------------------------- ##

## Command line parsing
parser = argparse.ArgumentParser(
    description="Analyzes HBP data and generates plots."
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

args = parser.parse_args()

## Read and update configuration
config = ConfigReader(basic.verify_file_path(basic.sanitize_path(const.DEFAULT_CONFIG_INI_FILE)))

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
    
## Directories
plot_dir  = config.get("paths", "plot_dir")
skeet_dir = config.get("paths", "skeet_dir")
video_dir = config.get("paths", "video_dir")



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
        print(f" ⚾ {config.get('app', 'name')} ⚾ ~~> 📊 Plotter")
        print("="*80)
        start_time = time.time()

## The plan:
##  1. Get a list of all current skeets in skeet_dir waiting to go.
##  2. Skip any files that don't end in '_desc.txt'
##  3. Check if it's already been skeeted. If so, remove all files.
##  4. Query the play_id. This is 'current_play'.
##  5. Extract the season, batter_id, and pitcher_id. 
##  6a. Query the season. This is 'all_season_data'.
##  6b. Query the batter_id. This is 'batter_career_data'.
##  6c. Query the pitcher_id. This is 'pitcher_career_data'.
##  7a. Plot all_season_data as gray, current_play color coded to end_speed.
##  7b. Plot batter_career_data as gray, current_play color coded to end_speed.
##  7c. Plot pitcher_career_data as gray, current_play color coded to end_speed.

        ## 1. Get a list of all current skeets in skeet_dir waiting to go.
        skeet_dir_files = sorted(os.listdir(skeet_dir))
        if verbose:
            pprint.pprint(skeet_dir_files)
            
        for skeet_file in skeet_dir_files:
            full_skeet_filename = Path(skeet_dir, skeet_file)
            skeet_root, ext     = os.path.splitext(skeet_file)        
            skeet_parts         = skeet_root.split('_')

            ## Not a file we want to work with
            if not skeet_parts[0].isdigit():
                print()
                continue

            game_pk = skeet_parts[0]
            play_id = skeet_parts[1]
            print(f"⚾ Game = {game_pk}, Play ID = {play_id}")

            ## 2. Skip any files that don't end in '_desc.txt'
            if skeet_parts[1] == "clean":
                ## We don't skeet out games where there are no HBP events.
                print(f"  😞 Nobody got hit during this game. Skipping.\n")
                os.remove(full_skeet_filename)
                continue
            elif skeet_parts[1] == "analyze":
                print(f"  😒 Current file is analysis information. Skipping.\n")
                continue

            ## 3. Check if it's already been skeeted. If so, remove all files.
            if dbmgr.has_been_skeeted(play_id):
                print(f"  🤨 This HBP has already been skeeted!\n")
                sk.cleanup_after_skeet(int(game_pk), play_id, verbose)
                continue
            
            ## 4. Query the play_id. This is 'current_play'.
            current_play = dbmgr.get_hbp_play_data(play_id)
            if verbose: 
                pprint.pprint(current_play)

            ##  5. Extract the season, batter_id, and pitcher_id. 
            game_date        = current_play[0][2]
            season,month,day = game_date.split('-')
            pitcher_info     = bb.get_mlb_player_details(current_play[0][3], verbose)
            batter_info      = bb.get_mlb_player_details(current_play[0][4], verbose)
            if verbose:                        
                pprint.pprint(pitcher_info)
                pprint.pprint(batter_info)

            ##  6. Query the season, pitcher_id, batter_id.
            all_season_data     = dbmgr.get_season_data(int(season))
            pitcher_career_data = dbmgr.get_all_pitcher_data(pitcher_info['id'])
            batter_career_data  = dbmgr.get_all_batter_data(batter_info['id'])
            print(f"   In {season} there have been {len(all_season_data)} HBP events.")
            print(f"   {pitcher_info['name']} ({pitcher_info['primary_position']}) has hit {len(pitcher_career_data)} batters in his career.")
            print(f"   {batter_info['name']} ({batter_info['primary_position']}) has been hit {len(batter_career_data)} times in his career.")



##  7a. Plot all_season_data as gray, current_play color coded to end_speed.
##  7b. Plot batter_career_data as gray, current_play color coded to end_speed.
##  7c. Plot pitcher_career_data as gray, current_play color coded to end_speed.










            print()

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
