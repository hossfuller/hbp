#!/usr/bin/env python3

## -------------------------------------------------------------------------- ##
## HBP Downloader
## Using statcast data, builds a skeet and downloads the video. Also updates
## the HBP database for the plotter script.
## -------------------------------------------------------------------------- ##


import argparse
import json
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

from atproto import Client, client_utils, models
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


## -------------------------------------------------------------------------- ##
## SETUP
## -------------------------------------------------------------------------- ##

## Command line parsing
parser = argparse.ArgumentParser(
    description="Posts skeets and videos to Bluesky."
)
parser.add_argument(
    "-p",
    "--num-posts",
    type=int,
    default=1,
    help="Number of HBP events to post. Defaults to '%(default)s'.",
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

num_posts = config.get("bluesky", "num_posts_per_run")
if args.num_posts:
    config.set("bluesky", "num_posts_per_run", str(args.num_posts))
    num_posts = args.num_posts

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
        config.get("logging", "skeeter_prefix"),
    )

## Directories
plot_dir  = config.get("paths", "plot_dir")
skeet_dir = config.get("paths", "skeet_dir")
video_dir = config.get("paths", "video_dir")


## -------------------------------------------------------------------------- ##
## MAIN ACTION
## -------------------------------------------------------------------------- ##

def main(num_posts: Optional[int] = 1) -> int:
    try:
        print()

        if verbose:
            print(config.get_all())
            print()

        print("="*80)
        print(f" ⚾ {config.get('app', 'name')} ⚾ ~~> 🦋 Bluesky Skeeter")
        print("="*80)
        start_time = time.time()

        ## -----------------------
        ## Bluesky Setup
        ## -----------------------
        # bsky_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        bsky_user = config.get("bluesky", "username")
        bsky_pass = None
        pwd_file = Path(const.DEFAULT_CONFIG_DIRECTORY, config.get("bluesky", "pwd_file"))
        with open(pwd_file, 'r', encoding='utf-8') as f:
            bsky_pass = f.read()
    
        print(f"🔌 Connecting to bluesky account for {bsky_user}...")
        client = Client()
        try:
            profile = client.login(bsky_user, bsky_pass)
        except:
            raise Exception("❌ Unable to connect to Bluesky!!")        

        print(f"👍 Connected as '{profile.handle}'.")
        if double_verbose:
            print()
            pprint.pprint(profile)
        print()

        ## -----------------------
        ## Skeet loop
        ## -----------------------
        skeet_dir_files = sorted(os.listdir(skeet_dir))
        if verbose:
            pprint.pprint(skeet_dir_files)
        if len(skeet_dir_files) < num_posts:
            print(f"‼️ Number of desired posts ({num_posts}) exceeds number of available skeets. Fixing.")
            num_posts = len(skeet_dir_files)
            print(f"‼️ Adjusted to {num_posts} posts. This may change during operation....")

        skeet_counter = 0
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

            if skeet_parts[1] == "clean":
                ## We don't skeet out games where there are no HBP events.
                print(f"  😞 Nobody got hit during this game. Skipping.\n")
                os.remove(full_skeet_filename)
                continue
            elif skeet_parts[1] == "analyze":
                print(f"  😒 Current file is analysis information. Skipping.\n")
                continue

            ## Now check if it's already been skeeted. If so, remove all files.
            if dbmgr.has_been_skeeted(play_id):
                print(f"  🤨 This HBP has already been skeeted!\n")
                sk.cleanup_after_skeet(int(game_pk), play_id, verbose)
                continue

            ## At this point, let's start building the skeet(s).
            ## 1. Get skeet text.
            if verbose:
                print(f"{i + 1}. Skeet File: {full_skeet_filename}")
            skeet_text = sk.read_skeet_text(full_skeet_filename)
            print(f"{skeet_text}")

            ## 2. Get video text.
            video_filepath = Path(video_dir, f"{game_pk}_{play_id}.mp4")
            if not dbmgr.has_been_downloaded(play_id) and not os.path.exists(video_filepath):
                ## Don't add a video!
                video_filepath = None
                print(f"  ⛔ No HBP video associated with this HBP!")
            elif not dbmgr.has_been_downloaded(play_id) and os.path.exists(video_filepath):
                ## File exists but hasn't been marked as downloaded!
                dbmgr.set_download_flag(play_id)
                print(f"  🤨 HBP video has been downloaded but not marked so in the database.")
            elif dbmgr.has_been_downloaded(play_id) and not os.path.exists(video_filepath):
                ## This is an error condition! File is missing.
                raise Exception(f"❌ Video {video_filepath} is missing!")
            elif dbmgr.has_been_downloaded(play_id) and os.path.exists(video_filepath):
                ## File has been marked as downloaded and does exist.
                pass        
            
            if video_filepath:
                print(f"🎥 Video file:     {video_filepath}")                

            ## 3. Get analysis plots and build plots data structures.
            plots = []
            plot_alts = []
            if dbmgr.has_been_analyzed(play_id):
                season       = dbmgr.get_season_year(play_id)
                current_play = dbmgr.get_hbp_play_data(play_id)
                pitcher_info = bb.get_mlb_player_details(current_play[0][3], verbose)
                batter_info  = bb.get_mlb_player_details(current_play[0][4], verbose)

                season_plot_filename  = Path(plot_dir, f"{game_pk}_{play_id}_{season}.png")
                batter_plot_filename  = Path(plot_dir, f"{game_pk}_{play_id}_batter.png")
                pitcher_plot_filename = Path(plot_dir, f"{game_pk}_{play_id}_pitcher.png")
                if os.path.exists(season_plot_filename):
                    plots.append(season_plot_filename)
                    plot_alts.append(f"Plot showing this HBP in the context of the entire {season} season.")
                    print(f"📊 Season's plot:  {season_plot_filename}")
                if os.path.exists(batter_plot_filename):
                    plots.append(batter_plot_filename)
                    plot_alts.append(f"Plot showing this HBP in the context of {batter_info['name']}'s entire career.")
                    print(f"📊 Batter's plot:  {batter_plot_filename}")
                if os.path.exists(pitcher_plot_filename):
                    plots.append(pitcher_plot_filename)
                    plot_alts.append(f"Plot showing this HBP in the context of {pitcher_info['name']}'s entire career.")
                    print(f"📊 Pitcher's plot: {pitcher_plot_filename}")

            ## 3. Use atproto client to construct and send skeet(s).
            try:
                if video_filepath:
                    vid_data = None
                    with open(video_filepath, 'rb') as f:
                        vid_data = f.read()
                    if vid_data:
                        root_post_ref = models.create_strong_ref(
                            client.send_video(
                                text=skeet_text,
                                video=vid_data,
                                video_alt=f"A video showing the hit-by-pitch at-bat."
                            )
                        )                        
                    else:
                        raise Exception(f"❌ Unable to read video file {video_filepath}!")
                else:
                    root_post_ref = models.create_strong_ref(client.send_post(skeet_text))
                    
                if plots:
                    images = []
                    for plot_path in plots:
                        with open(plot_path, 'rb') as f:
                            images.append(f.read())
                    
                    first_datetime_obj = datetime.strptime(dbmgr.get_earliest_date(), "%Y-%m-%d")
                    reply_to_root = models.create_strong_ref(
                        client.send_images(
                            text=f"Based on data collected through {first_datetime_obj.strftime("%d %b %Y")}.", 
                            images=images, 
                            image_alts=plot_alts,
                            reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref, root=root_post_ref),
                        )
                    )
            except:
                raise Exception(f"❌ Post of {play_id} failed!")
                            
            # 4. Clean up!
            if not test_mode:
                dbmgr.set_skeeted_flag(play_id)
                sk.cleanup_after_skeet(int(game_pk), play_id, verbose)
            
            print()
            skeet_counter = skeet_counter + 1
            if skeet_counter >= num_posts:
                break

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
    sys.exit(main(num_posts))
