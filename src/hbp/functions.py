#!/usr/bin/env python3

import pprint
import requests

from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

from . import constants as const


## -------------------------------------------------------------------------- ##
## DATE FUNCTIONS
## -------------------------------------------------------------------------- ##

def parse_date_string(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        msg = f"Not a valid date format: '{date_string}'. Expected format: YYYY-MM-DD."
        raise argparse.ArgumentTypeError(msg)


def subtract_one_day_from_date(date_str: Optional[str] = None):
    if date_str is None:
        return date.today() - timedelta(days=1)
    else:
        new_date = datetime.strptime(date_str, "%Y-%m-%d").date() - timedelta(days=1)
        return new_date.strftime("%Y-%m-%d")


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
    '''
    Stub function for reading a skeet file and returning its text.
    '''
    return ''


def write_skeet_text(game: list, event: list, skeet_dir: str, ind: Optional[int] = 4,verbose_bool: Optional[bool] = False) -> str:
    '''
    Stub function for writing skeet text to 'skeets/{game_pk}_{play_id}.txt' for
    HBP events and 'skeets/{game_pk}_clean.txt' for clean games.
    '''
    if verbose_bool:
        print("# --------- >")
        pprint.pprint(game)
        print("# ---")
        pprint.pprint(event)

    skeet_file_path = Path(skeet_dir, f"{game['game_pk']}_clean.txt")
    if len(event) > 0:
        skeet_file_path = Path(skeet_dir, f"{game['game_pk']}_{event['play_id']}.txt")

    winning_team  = game['away']['team']
    winning_score = game['away']['final_score']
    losing_score  = game['home']['final_score']
    if game['home']['final_score'] > game['away']['final_score']:
        winning_team  = game['home']['team']
        winning_score = game['home']['final_score']
        losing_score  = game['away']['final_score']

    game_datetime_object = datetime.strptime(game['date'], "%Y-%m-%d")
    game_date_string = game_datetime_object.strftime("%B %d, %Y")

    ## Base information
    multiline_skeet_string = \
f"""{game['away']['team']} ({game['away']['wins']}-{game['away']['losses']}) at {game['home']['team']} ({game['home']['wins']}-{game['home']['losses']})
{" "*ind}{game_date_string} ({game['description']})
"""

    ## HBP Event!!
    if len(event) > 0:
        multiline_skeet_string = multiline_skeet_string + f"""
⚾💥 {event['description']}
{' '*ind} Batter:  {build_mlb_player_display_string(event['batter'])}
{' '*ind} Pitcher: {build_mlb_player_display_string(event['pitcher'])}
{' '*ind} Count:   {build_hbp_event_count(event['at_bat'])}
{' '*ind} Pitch:   {build_hbp_event_pitch(event['at_bat'])}
"""
        if event['play_id'] is None or event['play_id'] == '':
            multiline_skeet_string = multiline_skeet_string + f"{' '*ind} Video unavailable"

    ## Nothing happened. Boo!
    else:
        multiline_skeet_string = multiline_skeet_string + f"""
{" "*ind}👍 Yay, nobody got hit!
"""

    ## Final score line.
    multiline_skeet_string = multiline_skeet_string + f"""
{" "*ind}{winning_team} won {winning_score}-{losing_score}
"""

    with open(skeet_file_path, 'w') as f:
        f.write(multiline_skeet_string)

    return skeet_file_path


## -------------------------------------------------------------------------- ##
## STATCAST FUNCTIONS
## -------------------------------------------------------------------------- ##

def convert_int_to_ordinal_str(n):
    n_str = str(n)
    if n_str[-1] == '1':
        n_str = n_str + 'st'
    elif n_str[-1] == '2':
        n_str = n_str + 'nd'
    elif n_str[-1] == '3':
        n_str = n_str + 'rd'
    else:
        n_str = n_str + 'th'
    return n_str


def build_hbp_event_count(at_bat_deets: list, verbose_bool: Optional[bool] = False) -> str:
    count_str = f"{at_bat_deets['balls']}-{at_bat_deets['strikes']}, {at_bat_deets['outs_when_up']} out"
    if at_bat_deets['outs_when_up'] != 1:
        count_str = count_str + 's'
    count_str = count_str + f", {at_bat_deets['half_inning'].lower()} of " + convert_int_to_ordinal_str(at_bat_deets['inning'])
    return count_str


def build_hbp_event_pitch(at_bat_deets: list, verbose_bool: Optional[bool] = False) -> str:
    effective_speed = (at_bat_deets['start_speed'] + at_bat_deets['end_speed'])/2.0
    return f"{effective_speed:.1f} mph {at_bat_deets['pitch_name'].lower()}"


def build_mlb_player_display_string(player: list, verbose_bool: Optional[bool] = False) -> str:
    player_string = f"{player['name']} ({player['hand']}) - {player['team']}"
    if verbose_bool:
        player_string = player_string + f" [id = {player['id']}]"
    return player_string


def get_mlb_game_deets(game: list, verbose_bool: Optional[bool] = False) -> list:
    '''
    Stub function for gathering basic details about the game in particular.
    '''
    game_deets = {
        'home': {
            'team'       : game['teams']['home']['team']['name'],
            'final_score': game['teams']['home']['score'],
            'wins'       : game['teams']['home']['leagueRecord']['wins'],
            'losses'     : game['teams']['home']['leagueRecord']['losses'],
            'pct'        : game['teams']['home']['leagueRecord']['pct'],
        },
        'away': {
            'team'       : game['teams']['away']['team']['name'],
            'final_score': game['teams']['away']['score'],
            'wins'       : game['teams']['away']['leagueRecord']['wins'],
            'losses'     : game['teams']['away']['leagueRecord']['losses'],
            'pct'        : game['teams']['away']['leagueRecord']['pct'],
        },
        'description': game['seriesDescription'],
        'date'       : game['officialDate'],
        'game_pk'    : game['gamePk'],
    }
    if verbose_bool:
        pprint.pprint(game)
        print("---------->")
        pprint.pprint(game_deets)

    return game_deets


def get_mlb_games_for_date(date_str: str, verbose_bool: Optional[bool] = False) -> list:
    url = const.MLB_STATS_BASE_URL + const.MLB_STATS_SCHEDULE_STUB
    params = {
        "sportId": 1,
        "date": date_str
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    games = []
    for date_block in data.get("dates", []):
        games.extend(date_block.get("games", []))
    return games


def get_mlb_hit_by_pitch_events_from_single_game(game: list, verbose_bool: Optional[bool] = False) -> list:
    hit_by_pitch_events = []

    live_feed_url = const.MLB_STATS_BASE_URL + game['link']
    response = requests.get(live_feed_url, timeout=10)
    response.raise_for_status()
    data = response.json()

    all_plays = data.get("liveData", {}).get("plays", {}).get("allPlays", [])

    for play in all_plays:
        # Identify HBP at the play-result level (most reliable)
        if play.get("result", {}).get("event") != "Hit By Pitch":
            continue

        # Find the final pitch event to extract play_id
        play_id = None
        pitch_events = [
            e for e in play.get("playEvents", [])
            if e.get("isPitch")
        ]

        if pitch_events:
            play_id = pitch_events[-1].get("playId")

        if verbose_bool:
            print("@@-- Start --@@")
            pprint.pprint(play['playEvents'][-1])
            print("@@--  End  --@@")

        hit_by_pitch_events.append({
            "game_pk"    : game['gamePk'],
            "play_id"    : play_id,
            "batter": {
                "id"  : play["matchup"]["batter"]["id"],
                "name": play["matchup"]["batter"]["fullName"],
                "hand": play["matchup"]["batSide"]["code"],
                "team": game['teams']['away']['team']['name'] if play["about"]["halfInning"] == "top" else game['teams']['home']['team']['name']
            },
            "pitcher": {
                "id"  : play["matchup"]["pitcher"]["id"],
                "name": play["matchup"]["pitcher"]["fullName"],
                "hand": play["matchup"]["pitchHand"]["code"],
                "team": game['teams']['away']['team']['name'] if play["about"]["halfInning"] == "bottom" else game['teams']['home']['team']['name']
            },
            "at_bat": {
                'balls'       : play['playEvents'][-1]["count"]["balls"],
                'strikes'     : play['playEvents'][-1]["count"]["strikes"],
                'outs_when_up': play['playEvents'][-1]["count"]["outs"],
                'inning'      : play["about"]["inning"],
                'half_inning' : play["about"]["halfInning"],
                'start_speed' : play['playEvents'][-1]['pitchData']['startSpeed'],
                'end_speed'   : play['playEvents'][-1]['pitchData']['endSpeed'],
                'pitch_name'  : play['playEvents'][-1]['details']['type']['description'],
            },
            "description": play['result']['description'],
        })

    return hit_by_pitch_events
