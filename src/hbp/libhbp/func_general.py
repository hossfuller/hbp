#!/usr/bin/env python3

import argparse
import ffmpeg
import os
import pprint
import requests

from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from pathlib import Path
from tqdm import tqdm
from typing import Optional

from . import basic as basic
from . import constants as const
from .configurator import ConfigReader


## -------------------------------------------------------------------------- ##
## GENERAL CONFIG
## -------------------------------------------------------------------------- ##

config    = ConfigReader(basic.verify_file_path(basic.sanitize_path(const.DEFAULT_CONFIG_INI_FILE)))
plot_dir  = config.get("paths", "plot_dir")
skeet_dir = config.get("paths", "skeet_dir")
video_dir = config.get("paths", "video_dir")


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

def download_baseball_savant_play(
    game_pk: str, 
    play_id: str, 
    verbose_bool: Optional[bool] = False, 
    video_dir: Optional[str] = video_dir
) -> str:
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


# ## Post: https://stackoverflow.com/a/64439347
# ## Working Gist: https://gist.github.com/ESWZY/a420a308d3118f21274a0bc3a6feb1ff
# def compress_video(video_full_path, size_upper_bound, two_pass=True, filename_suffix='_z'):
#     """
#     Compress video file to max-supported size.
#     :param video_full_path: the video you want to compress.
#     :param size_upper_bound: Max video size in KB.
#     :param two_pass: Set to True to enable two-pass calculation.
#     :param filename_suffix: Add a suffix for new video.
#     :return: out_put_name or error
#     """
#     filename, extension = os.path.splitext(video_full_path)
#     extension = '.mp4'
#     output_file_name = filename + filename_suffix + extension

#     # Adjust them to meet your minimum requirements (in bps), or maybe this function will refuse your video!
#     total_bitrate_lower_bound = 11000
#     min_audio_bitrate = 32000
#     max_audio_bitrate = 256000
#     min_video_bitrate = 100000

#     try:
#         # Bitrate reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
#         probe = ffmpeg.probe(video_full_path)
#         # Video duration, in s.
#         duration = float(probe['format']['duration'])
#         # Audio bitrate, in bps.
#         audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
#         # Target total bitrate, in bps.
#         target_total_bitrate = (size_upper_bound * 1024 * 8) / (1.073741824 * duration)
#         if target_total_bitrate < total_bitrate_lower_bound:
#             print('Bitrate is extremely low! Stop compress!')
#             return False

#         # Best min size, in kB.
#         best_min_size = (min_audio_bitrate + min_video_bitrate) * (1.073741824 * duration) / (8 * 1024)
#         if size_upper_bound < best_min_size:
#             print('Quality not good! Recommended minimum size:', '{:,}'.format(int(best_min_size)), 'KB.')
#             # return False

#         # Target audio bitrate, in bps.
#         audio_bitrate = audio_bitrate

#         # target audio bitrate, in bps
#         if 10 * audio_bitrate > target_total_bitrate:
#             audio_bitrate = target_total_bitrate / 10
#             if audio_bitrate < min_audio_bitrate < target_total_bitrate:
#                 audio_bitrate = min_audio_bitrate
#             elif audio_bitrate > max_audio_bitrate:
#                 audio_bitrate = max_audio_bitrate

#         # Target video bitrate, in bps.
#         video_bitrate = target_total_bitrate - audio_bitrate
#         if video_bitrate < 1000:
#             print('Bitrate {} is extremely low! Stop compress.'.format(video_bitrate))
#             return False

#         i = ffmpeg.input(video_full_path)
#         if two_pass:
#             ffmpeg.output(i, os.devnull,
#                           **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
#                           ).overwrite_output().run()
#             ffmpeg.output(i, output_file_name,
#                           **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
#                           ).overwrite_output().run()
#         else:
#             ffmpeg.output(i, output_file_name,
#                           **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}
#                           ).overwrite_output().run()

#         if os.path.getsize(output_file_name) <= size_upper_bound * 1024:
#             return output_file_name
#         elif os.path.getsize(output_file_name) < os.path.getsize(video_full_path):  # Do it again
#             return compress_video(output_file_name, size_upper_bound)
#         else:
#             return False
#     except FileNotFoundError as e:
#         print('You do not have ffmpeg installed!', e)
#         print('You can install ffmpeg by reading https://github.com/kkroening/ffmpeg-python/issues/251')
#         return False
   
    
# def find_smallest_video(
#     video_fullpath: str, 
#     max_size: Optional[int] = const.SKEETS_VIDEO_LIMIT,
#     verbose_bool: Optional[bool] = False
# ):
#     video_size_bytes = os.path.getsize(video_fullpath)
#     if video_size_bytes < max_size:
#         return video_fullpath
    
#     compressed_video_fullpath = video_fullpath.replace('.mp4', '_z.mp4')
#     if os.path.exists(compressed_video_fullpath):
#         compressed_video_size_bytes = os.path.getsize(compressed_video_fullpath)
#         if compressed_video_size_bytes < max_size:
#             return compressed_video_fullpath
#         else: 
#             return find_smallest_video(compressed_video_fullpath)
#     else:
#         return "Nope"

    