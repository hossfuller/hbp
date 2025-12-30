#!/bin/bash

## Hit By Pitches run script
## Author: Hossein Fuller <hossfuller@protonmail.com>
## Version: 1.0.0

## Change to the project directory.
cd "$(dirname "$0")"

## Set Python path and run the downloader with all command line arguments.
export PYTHONPATH="$(pwd)"
# python3 -m src.hbp.dbpopulator "$@"
# python3 -m src.hbp.downloader "$@"
python3 -m src.hbp.plotter "$@"
# python3 -m src.hbp.skeeter "$@"

