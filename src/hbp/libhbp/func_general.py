#!/usr/bin/env python3

import argparse
import os
import pprint
import requests

from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from pathlib import Path
from tqdm import tqdm
from typing import Optional

from . import constants as const
from .sqlitemgr import SQLiteManager


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
