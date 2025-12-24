#!/usr/bin/env python3

import os
import pprint
import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from pathlib import Path
from tqdm import tqdm
from typing import Optional

from . import constants as const
from . import func_baseball as bb

import libhbp.basic as libhbp
from libhbp.sqlitemgr import SQLiteManager


## -------------------------------------------------------------------------- ##
## DATABASE FUNCTIONS
## -------------------------------------------------------------------------- ##

def has_already_been_skeeted(play_id: str, dbfile: str, dbtable: Optional[str] = 'hbpdata') -> bool:
    already_skeeted = False
    with SQLiteManager(dbfile) as db: 
        select_data = db.get_hbpdata_data(
            f"SELECT * FROM {dbtable} WHERE play_id = ?",
            [play_id]
        )
    if len(select_data) == 1 and select_data[0][9] == 1:
        already_skeeted = True
    return already_skeeted


def remove_row(play_id: str, dbfile: str, dbtable: Optional[str] = 'hbpdata') -> bool:
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


def safe_dbinsert(game: list, event: list, dbfile: str, dbtable: Optional[str] = 'hbpdata') -> bool:
    safely_inserted = False
    with SQLiteManager(dbfile) as db: 
        select_data = db.get_hbpdata_data(
            f"SELECT * FROM {dbtable} WHERE play_id = ?",
            [event['play_id']]
        )
        if len(select_data) == 0:
            # print("Safe to insert!")
            db.insert_hbpdata(
                event['play_id'],              # play_id: str
                game['game_pk'],               # game_pk: str
                event['pitcher']['id'],        # pitcher_id: str
                event['batter']['id'],         # batter_id: str
                event['at_bat']['end_speed'],  # end_speed: float
                event['at_bat']['plate_x'],    # x_pos: float
                event['at_bat']['plate_z'],    # z_pos: float
            )
            safely_inserted = True
    return safely_inserted


def set_video_as_downloaded(play_id: str, dbfile: str, dbtable: Optional[str] = 'hbpdata') -> bool:
    marked = False
    with SQLiteManager(dbfile) as db: 
        update_data = db.update_hbpdata_data(
            f"UPDATE {dbtable} SET downloaded = 1 WHERE play_id = ?",
            [play_id]
        )
        if update_data == 0:
            raise Exception(f"Play ID {play_id} doesn't exist in the database!")
        elif update_data == 1:
            marked = True
        else:
            raise Exception("More than one entry was updated! THIS SHOULDN'T HAPPEN.")
    return marked


## -------------------------------------------------------------------------- ##
## DATE FUNCTIONS
## -------------------------------------------------------------------------- ##

def parse_date_string(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        msg = f"Not a valid date format: '{date_string}'. Expected format: YYYY-MM-DD."
        raise argparse.ArgumentTypeError(msg)


def add_one_day_to_date(date_str: Optional[str] = None):
    return transcend_time_and_space("forward", date_str)


def subtract_one_day_from_date(date_str: Optional[str] = None):
    return transcend_time_and_space("backward", date_str)


def transcend_time_and_space(direction: str, date_str: Optional[str] = None):
    return_date = None
    if date_str is None:
        if direction == "forward":
            return_date = date.today() + timedelta(days=1)
        else:
            return_date = date.today() - timedelta(days=1)
    else:
        if direction == "forward":
            new_date = datetime.strptime(str(date_str), "%Y-%m-%d").date() + timedelta(days=1)
        else:
            new_date = datetime.strptime(str(date_str), "%Y-%m-%d").date() - timedelta(days=1)
        return_date =  new_date.strftime("%Y-%m-%d")
    return return_date


## -------------------------------------------------------------------------- ##
## VIDEO FUNCTIONS
## -------------------------------------------------------------------------- ##

def download_baseball_savant_play(game_pk: str, play_id: str, video_dir: str, verbose_bool: Optional[bool] = False) -> str:
    page_url        = f"{const.BASEBALL_SAVANT_PLAY_VIDEO_URL}?playId={play_id}"
    video_url       = None
    video_file_path = None

    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        video_container = soup.find('div', class_='video-box')

        ## Download that sucker!
        if video_container:
            video_url       = video_container.find('video').find('source', type='video/mp4')['src']
            video_file_path = Path(video_dir, f"{game_pk}_{play_id}.mp4")

            if not os.path.exists(video_file_path):
                video_res = requests.get(video_url, stream=True)
                video_res.raise_for_status()

                ## https://stackoverflow.com/a/37573701
                total_size = int(video_res.headers.get('content-length', 0))
                chunk_size = 1024  # 1 KB chunks
                with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
                    with open(video_file_path, "wb") as file:
                        for data in video_res.iter_content(chunk_size):
                            progress_bar.update(len(data))
                            file.write(data)

                if total_size != 0 and progress_bar.n != total_size:
                    raise RuntimeError("Could not download file")

    except Exception as e:
        print(f"Error fetching video URL from {page_url}: {e}.")

    return video_file_path
