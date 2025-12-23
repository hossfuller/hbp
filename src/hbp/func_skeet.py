#!/usr/bin/env python3

import pprint

from datetime import datetime
from pathlib import Path
from typing import Optional

from . import constants as const
from . import func_baseball as bb


## -------------------------------------------------------------------------- ##
## SKEET FUNCTIONS
## -------------------------------------------------------------------------- ##

def delete_skeet_file(filename: str, verbose_bool: Optional[bool] = False) -> bool:
    '''
    Stub function that deletes skeet files.
    Returns true for success, false otherwise.
    '''
    return False


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
    date_str          = game_datetime_obj.strftime("%d %B %Y")

    ## If nobody got hit, add that to the skeet_strs list.
    if len(event) == 0:
        team_str           = f"⚾🧤 {game['away']['team']} at {game['home']['team']} 🧤⚾"
        nobody_got_hit_str = f"👍 Nobody got hit!"
        winning_team       = game['away']['team']
        winning_score      = game['away']['final_score']
        losing_score       = game['home']['final_score']
        if game['home']['final_score'] > game['away']['final_score']:
            winning_team  = game['home']['team']
            winning_score = game['home']['final_score']
            losing_score  = game['away']['final_score']
        winning_line_str = f"{winning_team} won {winning_score}-{losing_score}"

        skeet_strs = [team_str, date_str, nobody_got_hit_str, winning_line_str]

    ## Somebody got hit!
    else:
        team_str = f"⚾💥 {game['away']['team']} at {game['home']['team']} 💥⚾"
        batter_str   = f"Batter:  {bb.build_mlb_player_display_string(event['batter'])}"
        pitcher_str  = f"Pitcher: {bb.build_mlb_player_display_string(event['pitcher'])}"
        count_str    = f"Count:   {bb.build_hbp_event_count(event['at_bat'])}"
        pitch_str    = f"Pitch:   {bb.build_hbp_event_pitch(event['at_bat'])}"

        skeet_strs = [team_str, date_str, batter_str, pitcher_str, count_str, pitch_str]

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
