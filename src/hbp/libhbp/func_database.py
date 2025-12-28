#!/usr/bin/env python3

import pprint

from . import basic as basic
from . import constants as const
from .configurator import ConfigReader
from .sqlitemgr import SQLiteManager

from pathlib import Path


## -------------------------------------------------------------------------- ##
## DATABASE CONFIG
## -------------------------------------------------------------------------- ##

config       = ConfigReader(basic.verify_file_path(basic.sanitize_path(const.DEFAULT_CONFIG_INI_FILE)))
db_table     = config.get("database", "hbp_table")
db_file_path = Path(
    config.get("paths", "db_dir"), 
    config.get("database", "hbp_db_filename")
)


## -------------------------------------------------------------------------- ##
## DATABASE FUNCTIONS
## -------------------------------------------------------------------------- ##


def get_all_batter_data(player_id: int, dbfile: str = db_file_path, dbtable: str = db_table) -> list:
    return get_all_player_data(player_id, "batter", dbfile, dbtable)


def get_all_pitcher_data(player_id: int, dbfile: str = db_file_path, dbtable: str = db_table) -> list:
    return get_all_player_data(player_id, "pitcher", dbfile, dbtable)


def get_all_player_data(
    player_id: int, 
    player_type: str, 
    dbfile: str = db_file_path, 
    dbtable: str = db_table
) -> list:
    player_data = []
    
    player_types = ["batter", "pitcher"]
    if player_type not in player_types:
        return player_data

    with SQLiteManager(dbfile) as db: 
        player_data = db.query_hbpdata(
            f"SELECT * FROM {dbtable} WHERE {player_type}_id = ?",
            [player_id]
        )    
    return player_data


def get_hbp_play_data(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table):
    select_data = []
    with SQLiteManager(dbfile) as db: 
        select_data = db.query_hbpdata(
            f"SELECT * FROM {dbtable} WHERE play_id = ?",
            [play_id]
        )
    return select_data    
    
    
def get_season_data(season: int, dbfile: str = db_file_path, dbtable: str = db_table):
    season_data = []
    season_start = f"{season}-01-01"
    season_end = f"{season}-12-31"
    with SQLiteManager(dbfile) as db: 
        season_data = db.query_hbpdata(
            f"SELECT * FROM {dbtable} WHERE game_date BETWEEN ? AND ?",
            [season_start, season_end]
        )
    return season_data    

    
def has_been_downloaded(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table):
    return has_been_done(play_id, "downloaded", dbfile, dbtable)


def has_been_analyzed(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table):
    return has_been_done(play_id, "analyzed", dbfile, dbtable)


def has_been_skeeted(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table):
    return has_been_done(play_id, "skeeted", dbfile, dbtable)


def has_been_done(play_id: str, flag: str, dbfile: str = db_file_path, dbtable: str = db_table):
    flags       = {'downloaded': 8, 'analyzed': 9, 'skeeted': 10}
    flag_index  = flags.get(flag)
    flag_status = False
    
    if flag_status is not None:
        with SQLiteManager(dbfile) as db: 
            select_data = db.query_hbpdata(
                f"SELECT * FROM {dbtable} WHERE play_id = ?",
                [play_id]
            )
        if len(select_data) == 1 and select_data[0][flag_index] == 1:
            flag_status = True
    return flag_status


def set_download_flag(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table):
    return set_hbp_flag(play_id, 'downloaded', dbfile, dbtable)


def set_analyzed_flag(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table):
    return set_hbp_flag(play_id, 'analyzed', dbfile, dbtable)


def set_skeeted_flag(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table):
    return set_hbp_flag(play_id, 'skeeted', dbfile, dbtable)


def set_hbp_flag(play_id: str, flag: str, dbfile: str = db_file_path, dbtable: str = db_table):
    flags       = ['downloaded', 'analyzed', 'skeeted']
    flag_status = False

    if flag not in flags:
        return flag_status        
    
    with SQLiteManager(dbfile) as db: 
        update_data = db.update_hbpdata_data(
            f"UPDATE {dbtable} SET {flag} = 1 WHERE play_id = ?",
            [play_id]
        )
        if update_data == 0:
            raise Exception(f"Play ID {play_id} doesn't exist in the database!")
        elif update_data == 1:
            flag_status = True
        else:
            raise Exception("More than one entry was updated! THIS SHOULDN'T HAPPEN.")
    return flag_status


## -------------------------->
## DB Maintenance Funcs
## -------------------------->

def insert_row(game: list, event: list, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
    row_inserted = False
    select_data = get_hbp_play_data(event['play_id'])
    if len(select_data) == 0:
        with SQLiteManager(dbfile) as db: 
            db.insert_hbpdata(
                event['play_id'],              # play_id: str
                game['game_pk'],               # game_pk: str
                game['date'],                  # game_date: str
                event['pitcher']['id'],        # pitcher_id: str
                event['batter']['id'],         # batter_id: str
                event['at_bat']['end_speed'],  # end_speed: float
                event['at_bat']['plate_x'],    # x_pos: float
                event['at_bat']['plate_z'],    # z_pos: float
            )
            row_inserted = True
    return row_inserted


def remove_row(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
    deleted = False
    with SQLiteManager(dbfile) as db: 
        delete_data = db.update_hbpdata_data(
            f"DELETE FROM {dbtable} WHERE play_id = ?",
            [play_id]
        )
        if delete_data == 0 or delete_data == 1:
            deleted = True
        else:
            raise Exception("More than one entry was deleted! THIS SHOULDN'T HAPPEN.")
    return deleted
