#!/usr/bin/env python3

## -------------------------------------------------------------------------- ##
## @TODO Section!
## -------------------------------------------------------------------------- ##
# - Need to have a skeet-length check function!
# - Add a forward/backward flag to control the direction of hbp seek.
# - Add "{team} up X-Y" at moment of HBP
# - If the HBP triggers a score change, please note!
# - Download video (filename: 'videos/{game_pk}_{play_id}.txt')
## -------------------------------------------------------------------------- ##


import argparse
import pprint
import sys
import time

# Import application modules
from . import constants as const
from . import func_general as gen
from . import func_baseball as bb
from . import func_skeet as sk

import libhbp.basic
from libhbp.configurator import ConfigReader
from libhbp.logger import PrintLogger

from datetime import datetime, timedelta
from typing import Optional


## -------------------------------------------------------------------------- ##
## SETUP
## -------------------------------------------------------------------------- ##

## Command line parsing
parser = argparse.ArgumentParser(
    description="Finds HBP events, prepares skeets, and downloads videos."
)
parser.add_argument(
    "-c",
    "--config",
    type=libhbp.basic.verify_file_path,
    default="config/settings.ini",
    help="Override default config with custom settings file (default: '%(default)s').",
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

start_date = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
if args.date:
    start_date = args.date

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
        print(f" {config.get('app', 'name')} ~~> 💽 Downloader")
        print("="*80)
        start_time = time.time()

        found_hbp_events = False
        while not found_hbp_events:
            print()
            print(f'** Checking {start_date} for games...', end='')
            mlb_games = bb.get_mlb_games_for_date(start_date)
            print(f'found {len(mlb_games)}. **')
            if double_verbose:
                pprint.pprint(mlb_games)

            if len(mlb_games) == 0:
                start_date = gen.subtract_one_day_from_date(start_date)
                continue

            for index, game in enumerate(mlb_games):
                print()
                game_deets = bb.get_mlb_game_deets(game, double_verbose)

                if test_mode and index > 1:
                    break

                hbp_events = bb.get_mlb_hit_by_pitch_events_from_single_game(game, double_verbose)
                if hbp_events is None or len(hbp_events) == 0:
                    skeet_filename = sk.write_desc_skeet_text(game_deets, [], skeet_dir, double_verbose)
                    if verbose:
                        print(f"{index + 1}. Skeet File: {skeet_filename}")
                    skeet_text = sk.read_skeet_text(skeet_filename)
                    print(f"{skeet_text}")
                    continue

                if double_verbose:
                    pprint.pprint(hbp_events)

                for jndex, event in enumerate(hbp_events):
                    skeet_filename = sk.write_desc_skeet_text(game_deets, event, skeet_dir, double_verbose)
                    if verbose:
                        print(f"{index + 1}. Skeet File: {skeet_filename}")
                    skeet_text = sk.read_skeet_text(skeet_filename)
                    print(f"{skeet_text}")

                    if event['play_id'] is None or event['play_id'] == '':
                        print(f"😢 Video unavailable.")
                    else:
                        ## download video
                        video_filename = gen.download_baseball_savant_play(game['gamePk'], event['play_id'], video_dir, verbose)
                        print(f"VIDEO: {video_filename}")







            found_hbp_events = True
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
    sys.exit(main(start_date))
