#!/usr/bin/env python3

import pprint
import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

from . import constants as const
from . import func_baseball as bb


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
        if video_container:
            video_url = video_container.find('video').find('source', type='video/mp4')['src']




            video_file_path = Path(video_dir, f"{game_pk}_{play_id}.mp4")


    except Exception as e:
        print(f"Error fetching video URL from {page_url}: {e}.")

    return video_file_path
