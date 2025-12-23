#!/bin/bash

## Hit By Pitches run script
## Author: Hossein Fuller <hossfuller@protonmail.com>
## Version: 1.0.0

## Steps through the entire workflow from download to skeet.
## @todo: Remember to keep command line arguments consistent!!

## Change to the project directory.
cd "$(dirname "$0")"

## Set Python path and run the downloader with all command line arguments.
export PYTHONPATH="$(pwd)"
python3 -m src.hbp.downloader "$@"

# ## Figure out how to cram the plotter into this.
# export PYTHONPATH="$(pwd)"
# python3 -m src.hbp.plotter "$@"

# ## Run the skeeter.
# export PYTHONPATH="$(pwd)"
# python3 -m src.hbp.skeeter "$@"

