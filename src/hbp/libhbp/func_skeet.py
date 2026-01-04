#!/usr/bin/env python3

import os
import pprint
import random

from datetime import datetime
from pathlib import Path
from typing import Optional

from . import basic as basic
from . import constants as const
from . import func_baseball as bb
from .configurator import ConfigReader


## -------------------------------------------------------------------------- ##
## DIRECTORIES CONFIG
## -------------------------------------------------------------------------- ##

config    = ConfigReader(basic.verify_file_path(basic.sanitize_path(const.DEFAULT_CONFIG_INI_FILE)))
plot_dir  = config.get("paths", "plot_dir")
skeet_dir = config.get("paths", "skeet_dir")
video_dir = config.get("paths", "video_dir")


## -------------------------------------------------------------------------- ##
## SKEET FUNCTIONS
## -------------------------------------------------------------------------- ##

def cleanup_after_skeet(
    game_pk: int, 
    play_id: str, 
    verbose_bool: Optional[bool] = False, 
    plot_dir: Optional[str] = plot_dir,
    skeet_dir: Optional[str] = skeet_dir,
    video_dir: Optional[str] = video_dir
) -> list:
    files_removed = list()
    
    for plot_file in os.listdir(plot_dir):
        if plot_file.startswith(f"{game_pk}_{play_id}"):
            plot_filepath = Path(plot_dir, plot_file)
            os.remove(plot_filepath)
            files_removed.append(plot_filepath)

    for skeet_file in os.listdir(skeet_dir):
        if skeet_file.startswith(f"{game_pk}_{play_id}"):
            skeet_filepath = Path(skeet_dir, skeet_file)
            os.remove(skeet_filepath)
            files_removed.append(skeet_filepath)

    ## Remove video file.
    video_filepath = Path(video_dir, f"{game_pk}_{play_id}.mp4")
    if os.path.isfile(video_filepath):
        os.remove(video_filepath)
        files_removed.append(video_filepath)

    return files_removed


def read_skeet_text(filename: str, verbose_bool: Optional[bool] = False) -> str:
    file_contents = ''
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            file_contents = f.read()
    except FileNotFoundError:
        print(f"Error: '{filename}' was not found.")
    except Exception as e:
        print(f"Something bad happened: {e}")
    return file_contents


def write_desc_skeet_text(game: list, event: list, skeet_dir: str, verbose_bool: Optional[bool] = False) -> str:
    '''Returns the filename of the skeet, not the actual skeet!'''
    if verbose_bool:
        print("# --------- >")
        pprint.pprint(game)
        print("# ---")
        pprint.pprint(event)

    game_datetime_obj = datetime.strptime(game['date'], "%Y-%m-%d")
    date_str          = f"⚾💥 {game_datetime_obj.strftime("%d %B %Y")} 💥⚾"
    series_desc_str   = f"{game['description']}"

    ## If the game is finished, there'll be a final score.
    if 'final_score' in game['home']:
        winning_team       = game['away']['team']
        winning_score      = game['away']['final_score']
        losing_score       = game['home']['final_score']
        if game['home']['final_score'] > game['away']['final_score']:
            winning_team  = game['home']['team']
            winning_score = game['home']['final_score']
            losing_score  = game['away']['final_score']

    ## If nobody got hit, add that to the skeet_strs list.
    if len(event) == 0:
        team_str           = f"⚾🧤 {game['away']['team']} at {game['home']['team']} 🧤⚾"
        nobody_got_hit_str = f"👍 Nobody got hit!"
        
        winning_line_str = ''
        if 'final_score' in game['home']: 
            winning_line_str = f"{winning_team} won {winning_score}-{losing_score} in {game['innings']} innings"  
            
        skeet_strs = [team_str, date_str, series_desc_str, nobody_got_hit_str, winning_line_str]

    ## Somebody got hit!
    else:
        game_is_tied   = False
        leading_team   = game['away']['team']
        leading_score  = event['at_bat']['away_score']
        trailing_score = event['at_bat']['home_score']
        if event['at_bat']['home_score'] > event['at_bat']['away_score']:
            leading_team   = game['home']['team']
            leading_score  = event['at_bat']['home_score']
            trailing_score = event['at_bat']['away_score']
        elif event['at_bat']['home_score'] == event['at_bat']['away_score']:
            game_is_tied = True

        teamname_str = bb.get_mlb_team_attribute(leading_team, 'teamname')
        if teamname_str is None:
            teamname_str = leading_team
        score_str   = f"{teamname_str} up {leading_score}-{trailing_score}"
        if game_is_tied: 
            score_str = f"tied at {leading_score}-{trailing_score}"

        batter_str      = f"Batter: {bb.build_mlb_player_display_string(event['batter'])}"
        pitcher_str     = f"Pitcher: {bb.build_mlb_player_display_string(event['pitcher'])}"
        count_str       = f"The Play: {bb.build_hbp_event_count(event['at_bat'])}, {score_str}"
        pitch_str       = f"The Pitch: {bb.build_hbp_event_pitch(event['at_bat'])}"

        final_score_str = ''
        if 'final_score' in game['home']: 
            final_score_str = f"Final: {winning_team} won {winning_score}-{losing_score} in {game['innings']} innings."

        skeet_strs = [date_str, series_desc_str, pitcher_str, batter_str, count_str, pitch_str, final_score_str]

    total_skeet_str = "\n".join(skeet_strs)
    total_skeet_length = len(total_skeet_str)
    if total_skeet_length > const.SKEETS_CHAR_LIMIT:
        raise Exception("Basic skeet text is already too long!")

    ## Build filename
    skeet_file_path = Path(skeet_dir, f"{game['game_pk']}_clean.txt")
    if len(event) > 0:
        skeet_file_path = Path(skeet_dir, f"{game['game_pk']}_{event['play_id']}_desc.txt")

    with open(skeet_file_path, 'w', encoding='utf-8') as f:
        f.write(total_skeet_str)

    return skeet_file_path
